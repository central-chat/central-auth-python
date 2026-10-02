"""Mints Central App Entry tokens from the key file the console downloads."""

import json
import time
from typing import Optional

from jwcrypto import jwe, jwk, jws
from jwcrypto.common import json_encode

AUDIENCE = "central:app-entry"

# Central refuses a token whose exp is more than 300s past its iat.
TTL_SECONDS = 300

_REQUIRED = ("kid", "alg", "iss", "privateJwk", "centralEncryptionKey")


class CentralAuth:
    def __init__(self, bundle: dict):
        missing = [field for field in _REQUIRED if not bundle.get(field)]
        if missing:
            raise ValueError(f"CentralAuth bundle is missing {', '.join(missing)}")
        self._bundle = bundle

    @classmethod
    def from_file(cls, path: str) -> "CentralAuth":
        """Reads the certificate file the console downloaded."""
        with open(path, encoding="utf-8") as handle:
            return cls(json.load(handle))

    def mint_token(self, user_id: str, claims: Optional[dict] = None) -> str:
        """Mints the entry token for one person: a JWS signed with your key, wrapped in a JWE only Central can open.

        `user_id` is the identity Central logs in, so it must come from your own
        session and never from the request; `claims` takes `userName`.
        """
        if not user_id:
            raise ValueError("mint_token needs a user_id")

        user_name = (claims or {}).get("userName")
        bundle = self._bundle
        recipient = bundle["centralEncryptionKey"]
        now = int(time.time())

        claims = {
            "iss": bundle["iss"],
            "sub": str(user_id),
            "aud": AUDIENCE,
            "iat": now,
            "exp": now + TTL_SECONDS,
            "chat_account": bundle["kid"],
        }
        # `userName` travels as the `name` claim, which is what Central reads.
        if user_name:
            claims["name"] = user_name

        signature = jws.JWS(json_encode(claims))
        signature.add_signature(
            jwk.JWK(**bundle["privateJwk"]),
            alg=bundle["alg"],
            protected=json_encode({"alg": bundle["alg"], "kid": bundle["kid"], "typ": "JWT"}),
        )

        # bid/cid ride the JWE header so the embedded widget can route on the
        # token alone, without the page repeating the ids.
        encrypted = jwe.JWE(
            signature.serialize(compact=True).encode("utf-8"),
            protected=json_encode(
                {
                    "alg": recipient["alg"],
                    "enc": "A256GCM",
                    "cty": "JWT",
                    "kid": recipient["kid"],
                    "bid": bundle["iss"],
                    "cid": bundle["kid"],
                }
            ),
        )
        encrypted.add_recipient(jwk.JWK(**recipient["publicJwk"]))
        return encrypted.serialize(compact=True)

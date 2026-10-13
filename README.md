# central-auth

Mints [Central](https://central.chat) App Entry tokens: the JWT your backend
signs so the chat knows who just opened it. Server side only.

## Install

```sh
pip install central-auth
```

Python ≥ 3.9.

## Use

```python
from central_auth import CentralAuth

# The path to the certificate file you downloaded.
central = CentralAuth.from_file("./central-app-entry-<kid>.json")

token = central.mint_token(user_id, {"userName": user_name})
```

The certificate file is the one you download when you generate your
business's App Entry certificate. Nothing in it is copied by hand.

If the certificate lives in an env var or a secret manager, pass its content
instead: `CentralAuth.from_string(os.environ["CENTRAL_APP_ENTRY_CERT_JSON"])`.

`user_id` is the identity Central logs in, so it must come from your own session
and never from the request: whoever can choose it signs in as that person.

The token is valid for 300 seconds, which is the protocol ceiling — mint one per
entry rather than caching it.
## Try it

`examples/mint_token.py` mints one token so you can check a certificate without
editing anything — the path comes from the environment:

```sh
pip install -e .
CENTRAL_APP_ENTRY_CERT=./central-app-entry-<kid>.json python examples/mint_token.py
```

`CENTRAL_USER_ID` and `CENTRAL_USER_NAME` are optional.

## License

Apache-2.0

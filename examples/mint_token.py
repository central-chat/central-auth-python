"""Mints one token, to check a certificate end to end without editing any code.

    CENTRAL_APP_ENTRY_CERT=./central-app-entry-<kid>.json python examples/mint_token.py

CENTRAL_USER_ID and CENTRAL_USER_NAME are optional. The token prints to stdout
and lasts 300 seconds.

Install the package first (`pip install -e .`): the module lives under src/, so
it resolves from site-packages and never from this directory.
"""

import os
import sys

from central_auth import CentralAuth

cert_path = os.environ.get("CENTRAL_APP_ENTRY_CERT")
if not cert_path:
    sys.exit("Set CENTRAL_APP_ENTRY_CERT to the certificate file the console downloaded.")

central = CentralAuth.from_file(cert_path)

print(central.mint_token(
    os.environ.get("CENTRAL_USER_ID", "example-user"),
    {"userName": os.environ.get("CENTRAL_USER_NAME")},
))

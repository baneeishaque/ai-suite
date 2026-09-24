#!/usr/bin/env python3
"""
oauth-setup.py — Full PKCE OAuth2 setup flow for Google APIs.

Generates a PKCE auth URL, reads the user's authorization code from stdin,
exchanges it for tokens, and saves the credential cache.

Usage:
    python3 oauth-setup.py \\
        --client-secrets /path/to/client_secrets.json \\
        --scopes "https://www.googleapis.com/auth/youtube" \\
        --output /path/to/credentials.json
"""
import argparse
import base64
import hashlib
import json
import secrets
import sys
from urllib.parse import urlencode

import requests


def parse_args():
    parser = argparse.ArgumentParser(description="Google OAuth2 PKCE setup")
    parser.add_argument("--client-secrets", required=True, help="Path to client_secrets.json")
    parser.add_argument("--scopes", nargs="+", required=True, help="Google API scopes")
    parser.add_argument("--output", required=True, help="Path to write credential cache")
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.client_secrets) as f:
        client_data = json.load(f)

    if "installed" in client_data:
        client_id = client_data["installed"]["client_id"]
        client_secret = client_data["installed"]["client_secret"]
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    elif "web" in client_data:
        client_id = client_data["web"]["client_id"]
        client_secret = client_data["web"]["client_secret"]
        print("WARNING: 'web' client type detected. The OOB redirect URI may not work.", file=sys.stderr)
        redirect_uri = client_data["web"]["redirect_uris"][0]
    else:
        print("ERROR: client_secrets.json must contain 'installed' or 'web' key", file=sys.stderr)
        sys.exit(1)

    scope_string = " ".join(args.scopes)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode()

    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope_string,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = "https://accounts.google.com/o/oauth2/auth?" + urlencode(auth_params)

    print("=" * 60)
    print("Open this URL in your browser and sign in:")
    print(auth_url)
    print("=" * 60)

    code = input("Paste the authorization code: ").strip()

    token_endpoint = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
    }
    resp = requests.post(token_endpoint, data=token_data)
    if resp.status_code != 200:
        print(f"ERROR: Token exchange failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)

    tokens = resp.json()

    credential_cache = {
        "access_token": tokens["access_token"],
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": tokens.get("refresh_token", ""),
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": scope_string.split(),
        "token_response": tokens,
    }

    with open(args.output, "w") as f:
        json.dump(credential_cache, f, indent=2)

    print(f"Credentials saved to: {args.output}")
    has_refresh = bool(tokens.get("refresh_token"))
    print(f"Has refresh_token: {has_refresh}")


if __name__ == "__main__":
    main()

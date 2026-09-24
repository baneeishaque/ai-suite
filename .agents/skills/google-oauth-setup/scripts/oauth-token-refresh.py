#!/usr/bin/env python3
"""
oauth-token-refresh.py — Refresh an expired Google OAuth access token.

Reads existing credentials, exchanges the refresh_token for a new access_token,
and writes the updated cache. Exits 1 if the refresh_token has expired.

Usage:
    python3 oauth-token-refresh.py \\
        --client-secrets /path/to/client_secrets.json \\
        --credentials /path/to/credentials.json \\
        --output /path/to/credentials.json
"""
import argparse
import json
import sys

import requests


def parse_args():
    parser = argparse.ArgumentParser(description="Refresh Google OAuth token")
    parser.add_argument("--client-secrets", required=True, help="Path to client_secrets.json")
    parser.add_argument("--credentials", required=True, help="Path to existing credential cache")
    parser.add_argument("--output", required=True, help="Path to write refreshed credentials")
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.client_secrets) as f:
        client_data = json.load(f)
    key = "installed" if "installed" in client_data else "web"
    client_id = client_data[key]["client_id"]
    client_secret = client_data[key]["client_secret"]

    with open(args.credentials) as f:
        creds = json.load(f)

    refresh_token = creds.get("refresh_token") or creds.get("refreshToken", "")
    if not refresh_token:
        print("ERROR: No refresh_token found in credentials", file=sys.stderr)
        sys.exit(1)

    token_endpoint = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    resp = requests.post(token_endpoint, data=token_data)
    if resp.status_code != 200:
        print(f"ERROR: Token refresh failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)

    tokens = resp.json()

    creds["access_token"] = tokens["access_token"]
    creds["token_response"] = tokens
    if "expiry" in creds:
        creds.pop("expiry", None)

    with open(args.output, "w") as f:
        json.dump(creds, f, indent=2)

    print(f"Token refreshed and saved to: {args.output}")


if __name__ == "__main__":
    main()

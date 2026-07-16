#!/usr/bin/env python3
"""
Authentication helper for Microsoft Graph API using Azure Identity.
Supports device code flow and token caching for delegated authentication.
"""

import os
import json
from pathlib import Path
from typing import Optional

from azure.identity import DeviceCodeCredential, TokenCachePersistenceOptions
from msgraph import GraphServiceClient


DEFAULT_CACHE_PATH = Path.home() / ".msgraph-token-cache.json"
DEFAULT_SCOPES = ["https://graph.microsoft.com/.default"]


def get_credential(
    tenant_id: Optional[str] = None,
    client_id: Optional[str] = None,
    cache_path: Optional[Path] = None,
    use_device_code: bool = True,
) -> DeviceCodeCredential:
    """
    Create a DeviceCodeCredential with token caching.
    
    Args:
        tenant_id: Azure AD tenant ID (optional, uses common endpoint if not provided)
        client_id: Azure AD app client ID (required for device code flow)
        cache_path: Path to token cache file
        use_device_code: Whether to use device code flow (always True for this credential type)
    
    Returns:
        DeviceCodeCredential configured with caching
    """
    cache_path = cache_path or DEFAULT_CACHE_PATH
    
    cache_options = TokenCachePersistenceOptions(
        name=str(cache_path),
        allow_unencrypted_storage=True,
    )
    
    return DeviceCodeCredential(
        tenant_id=tenant_id or "common",
        client_id=client_id,
        cache_persistence_options=cache_options,
    )


def get_graph_client(
    credential: DeviceCodeCredential,
    scopes: Optional[list[str]] = None,
) -> GraphServiceClient:
    """
    Create a GraphServiceClient with the given credential.
    
    Args:
        credential: Authenticated credential
        scopes: OAuth scopes (defaults to Graph default)
    
    Returns:
        Configured GraphServiceClient
    """
    scopes = scopes or DEFAULT_SCOPES
    return GraphServiceClient(credentials=credential, scopes=scopes)


async def get_access_token(
    credential: DeviceCodeCredential,
    scopes: Optional[list[str]] = None,
) -> str:
    """
    Get an access token from the credential.
    
    Args:
        credential: DeviceCodeCredential instance
        scopes: OAuth scopes
    
    Returns:
        Access token string
    """
    scopes = scopes or DEFAULT_SCOPES
    token = await credential.get_token(*scopes)
    return token.token


def clear_token_cache(cache_path: Optional[Path] = None) -> None:
    """Clear the token cache file."""
    cache_path = cache_path or DEFAULT_CACHE_PATH
    if cache_path.exists():
        cache_path.unlink()


def has_cached_token(cache_path: Optional[Path] = None) -> bool:
    """Check if a valid token cache exists."""
    cache_path = cache_path or DEFAULT_CACHE_PATH
    if not cache_path.exists():
        return False
    try:
        with open(cache_path) as f:
            data = json.load(f)
        return bool(data.get("AccessToken"))
    except Exception:
        return False


if __name__ == "__main__":
    # Test authentication
    import asyncio
    
    async def test():
        cred = get_credential(client_id="YOUR_CLIENT_ID")
        token = await get_access_token(cred)
        print(f"Token acquired: {token[:20]}...")
    
    asyncio.run(test())

#!/usr/bin/env python3
"""
Microsoft Graph File Download CLI
Downloads files from Microsoft Graph (OneDrive/SharePoint/Teams) using delegated auth.
Outputs JSON Lines with file metadata and local paths.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import quote

# Add parent directory to path for auth_helper import
sys.path.insert(0, str(Path(__file__).parent))

from auth_helper import get_credential, get_graph_client, get_access_token, has_cached_token


async def download_file(
    client: GraphServiceClient,
    drive_id: str,
    item_id: str,
    output_dir: Path,
    metadata_only: bool = False,
) -> dict:
    """
    Download a single file from Microsoft Graph.
    
    Args:
        client: Authenticated GraphServiceClient
        drive_id: Drive ID
        item_id: Item ID or path (e.g., "root:/Documents/file.docx")
        output_dir: Output directory
        metadata_only: Only fetch metadata, skip content download
    
    Returns:
        Dict with file metadata and status
    """
    result = {
        "item_id": item_id,
        "name": "",
        "path": "",
        "size": 0,
        "etag": "",
        "last_modified": "",
        "download_url": "",
        "local_path": "",
        "status": "pending",
    }
    
    try:
        # Determine if item_id is a path (starts with "root:") or an ID
        if item_id.startswith("root:"):
            # Get item by path
            path_part = item_id[5:]  # Remove "root:"
            item = await client.drives.by_drive_id(drive_id).root.get_by_path(path_part).get()
            result["path"] = path_part
        else:
            # Get item by ID
            item = await client.drives.by_drive_id(drive_id).items.by_item_id(item_id).get()
        
        if not item:
            result["status"] = "error"
            result["error"] = "Item not found"
            return result
        
        # Extract metadata
        result["name"] = item.name or ""
        result["size"] = item.size or 0
        result["etag"] = item.e_tag or ""
        result["last_modified"] = item.last_modified_date_time.isoformat() if item.last_modified_date_time else ""
        
        # Get download URL (for reference)
        if item.additional_data and "@microsoft.graph.downloadUrl" in item.additional_data:
            result["download_url"] = item.additional_data["@microsoft.graph.downloadUrl"]
        
        if metadata_only:
            result["status"] = "success"
            return result
        
        # Download content
        # Use the content endpoint which handles redirects
        if item_id.startswith("root:"):
            content_response = await client.drives.by_drive_id(drive_id).root.get_by_path(path_part).content.get()
        else:
            content_response = await client.drives.by_drive_id(drive_id).items.by_item_id(item_id).content.get()
        
        if not content_response:
            result["status"] = "error"
            result["error"] = "No content returned"
            return result
        
        # Determine output path
        # Preserve folder structure from the path
        if result["path"]:
            relative_path = Path(result["path"]).parent / result["name"]
        else:
            relative_path = Path(result["name"])
        
        local_path = output_dir / relative_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        content = await content_response.read()
        local_path.write_bytes(content)
        
        result["local_path"] = str(local_path)
        result["status"] = "success"
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result


async def main():
    parser = argparse.ArgumentParser(
        description="Download files from Microsoft Graph API (OneDrive/SharePoint/Teams)"
    )
    parser.add_argument(
        "--drive-id",
        required=True,
        help="Microsoft Graph drive ID",
    )
    parser.add_argument(
        "--item-ids",
        nargs="+",
        required=True,
        help="Item IDs or paths (e.g., 'root:/Documents/file.docx')",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Output directory for downloaded files",
    )
    parser.add_argument(
        "--access-token",
        help="Pre-authenticated access token (for automation)",
    )
    parser.add_argument(
        "--tenant-id",
        help="Azure AD tenant ID (for device code flow)",
    )
    parser.add_argument(
        "--client-id",
        help="Azure AD app client ID (for device code flow)",
    )
    parser.add_argument(
        "--use-device-code",
        action="store_true",
        help="Force device code flow even if token provided",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Only fetch metadata (ETag, lastModifiedDateTime), skip content download",
    )
    parser.add_argument(
        "--cache-path",
        type=Path,
        default=Path.home() / ".msgraph-token-cache.json",
        help="Token cache file path",
    )
    
    args = parser.parse_args()
    
    # Validate output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get credential and client
    if args.access_token and not args.use_device_code:
        # Use provided token directly
        from azure.core.credentials import AccessToken
        from azure.identity import AccessTokenCredential
        
        class StaticTokenCredential(AccessTokenCredential):
            def __init__(self, token: str):
                self._token = token
            
            def get_token(self, *scopes, **kwargs):
                return AccessToken(self._token, 9999999999)
        
        credential = StaticTokenCredential(args.access_token)
        client = get_graph_client(credential)
    else:
        # Use device code flow with caching
        if not args.client_id:
            print("Error: --client-id is required for device code flow", file=sys.stderr)
            sys.exit(1)
        
        # Check if we have cached token and not forcing device code
        if not args.use_device_code and has_cached_token(args.cache_path):
            print("Using cached token...", file=sys.stderr)
        
        credential = get_credential(
            tenant_id=args.tenant_id,
            client_id=args.client_id,
            cache_path=args.cache_path,
        )
        client = get_graph_client(credential)
    
    # Process each item
    for item_id in args.item_ids:
        result = await download_file(
            client=client,
            drive_id=args.drive_id,
            item_id=item_id,
            output_dir=args.output_dir,
            metadata_only=args.metadata_only,
        )
        # Output as JSON Line
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Validation script for OpenCode MCP configuration.
Checks that the mcp section in opencode.json follows the expected schema.
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

def load_opencode_config(file_path: str) -> Dict[Any, Any]:
    """Load OpenCode config file via opencode-jsonc-util base skill."""
    script_dir = Path(__file__).resolve().parent.parent.parent
    reader = script_dir / "opencode-jsonc-util" / "scripts" / "read-jsonc.py"
    if not reader.exists():
        print(f"ERROR: opencode-jsonc-util not found at {reader}", file=sys.stderr)
        print("Install the base skill: .agents/skills/opencode-jsonc-util/", file=sys.stderr)
        sys.exit(1)
    try:
        result = subprocess.run(
            [sys.executable, str(reader), file_path],
            capture_output=True, text=True, check=True, timeout=10
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: opencode-jsonc-util failed: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: opencode-jsonc-util timed out", file=sys.stderr)
        sys.exit(1)

def validate_mcp_section(config: Dict[Any, Any]) -> List[str]:
    """Validate the mcp section of OpenCode config."""
    errors = []
    
    if 'mcp' not in config:
        # This is not necessarily an error - mcp section is optional
        return errors
    
    mcp_section = config['mcp']
    if not isinstance(mcp_section, dict):
        errors.append("'mcp' section must be an object")
        return errors
    
    for server_name, server_config in mcp_section.items():
        if not isinstance(server_config, dict):
            errors.append(f"MCP server '{server_name}' must be an object")
            continue
        
        # Check type field
        if 'type' not in server_config:
            errors.append(f"MCP server '{server_name}' missing required 'type' field")
            continue
        
        server_type = server_config['type']
        if server_type not in ['local', 'remote']:
            errors.append(f"MCP server '{server_name}' has invalid type '{server_type}' (must be 'local' or 'remote')")
            continue
        
        # Validate based on type
        if server_type == 'local':
            errors.extend(_validate_local_server(server_name, server_config))
        elif server_type == 'remote':
            errors.extend(_validate_remote_server(server_name, server_config))
    
    return errors

def _validate_local_server(server_name: str, config: Dict[Any, Any]) -> List[str]:
    """Validate a local (stdio) MCP server configuration."""
    errors = []
    
    # Required fields for local servers
    if 'command' not in config:
        errors.append(f"Local MCP server '{server_name}' missing required 'command' field")
    elif not isinstance(config['command'], str):
        errors.append(f"Local MCP server '{server_name}' 'command' must be a string")
    
    if 'args' not in config:
        errors.append(f"Local MCP server '{server_name}' missing required 'args' field")
    elif not isinstance(config['args'], list):
        errors.append(f"Local MCP server '{server_name}' 'args' must be an array")
    else:
        for i, arg in enumerate(config['args']):
            if not isinstance(arg, str):
                errors.append(f"Local MCP server '{server_name}' args[{i}] must be a string")
    
    # Optional env field
    if 'env' in config and not isinstance(config['env'], dict):
        errors.append(f"Local MCP server '{server_name}' 'env' must be an object if present")
    
    # Optional enabled field
    if 'enabled' in config and not isinstance(config['enabled'], bool):
        errors.append(f"Local MCP server '{server_name}' 'enabled' must be a boolean if present")
    
    return errors

def _validate_remote_server(server_name: str, config: Dict[Any, Any]) -> List[str]:
    """Validate a remote (HTTP/WebSocket) MCP server configuration."""
    errors = []
    
    # Required fields for remote servers
    if 'url' not in config:
        errors.append(f"Remote MCP server '{server_name}' missing required 'url' field")
    elif not isinstance(config['url'], str):
        errors.append(f"Remote MCP server '{server_name}' 'url' must be a string")
    elif not config['url'].startswith(('http://', 'https://', 'ws://', 'wss://')):
        errors.append(f"Remote MCP server '{server_name}' 'url' must be a valid HTTP/WebSocket URL")
    
    # Check auth method - either headers or oauth should be present
    has_headers = 'headers' in config and isinstance(config['headers'], dict)
    has_oauth = 'oauth' in config and isinstance(config['oauth'], dict)
    
    if not has_headers and not has_oauth:
        errors.append(f"Remote MCP server '{server_name}' must have either 'headers' or 'oauth' field for authentication")
    
    # Validate headers if present
    if has_headers:
        headers = config['headers']
        if not isinstance(headers, dict):
            errors.append(f"Remote MCP server '{server_name}' 'headers' must be an object")
        else:
            # Check for Authorization header
            if 'Authorization' not in headers:
                errors.append(f"Remote MCP server '{server_name}' headers should typically include 'Authorization' field")
            else:
                auth_value = headers['Authorization']
                if not isinstance(auth_value, str):
                    errors.append(f"Remote MCP server '{server_name}' headers.Authorization must be a string")
                # Check for env var interpolation
                elif '{env:' in auth_value and '}' not in auth_value:
                    errors.append(f"Remote MCP server '{server_name}' headers.Authorization has malformed env var interpolation")
    
    # Validate oauth if present
    if has_oauth:
        oauth = config['oauth']
        if not isinstance(oauth, dict):
            errors.append(f"Remote MCP server '{server_name}' 'oauth' must be an object")
        else:
            required_oauth_fields = ['clientId', 'clientSecret', 'tokenUrl']
            for field in required_oauth_fields:
                if field not in oauth:
                    errors.append(f"Remote MCP server '{server_name}' oauth missing required '{field}' field")
                elif not isinstance(oauth[field], str):
                    errors.append(f"Remote MCP server '{server_name}' oauth.{field} must be a string")
            
            # Validate scopes if present
            if 'scopes' in oauth:
                if not isinstance(oauth['scopes'], list):
                    errors.append(f"Remote MCP server '{server_name}' oauth.scopes must be an array if present")
                else:
                    for i, scope in enumerate(oauth['scopes']):
                        if not isinstance(scope, str):
                            errors.append(f"Remote MCP server '{server_name}' oauth.scopes[{i}] must be a string")
    
    # Optional enabled field
    if 'enabled' in config and not isinstance(config['enabled'], bool):
        errors.append(f"Remote MCP server '{server_name}' 'enabled' must be a boolean if present")
    
    return errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate-opencode-mcp.py <path-to-opencode.json>")
        print("Example: python validate-opencode-mcp.py ~/.config/opencode/opencode.json")
        sys.exit(1)
    
    config_path = os.path.expanduser(sys.argv[1])
    config = load_opencode_config(config_path)
    errors = validate_mcp_section(config)
    
    if errors:
        print("VALIDATION ERRORS:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("SUCCESS: OpenCode MCP configuration is valid")
        # Also show what we found
        if 'mcp' in config and config['mcp']:
            print("\nFound MCP servers:")
            for server_name, server_config in config['mcp'].items():
                server_type = server_config.get('type', 'unknown')
                print(f"  - {server_name} ({server_type})")
                if server_type == 'remote':
                    url = server_config.get('url', 'NO URL')
                    print(f"    URL: {url}")
                    if 'headers' in server_config:
                        auth = server_config['headers'].get('Authorization', 'NO AUTH HEADER')
                        # Redact token for display
                        if auth.startswith('Bearer ') and len(auth) > 15:
                            auth = 'Bearer [REDACTED]'
                        print(f"    Auth: {auth}")
        else:
            print("\nNo MCP servers configured")

if __name__ == '__main__':
    main()
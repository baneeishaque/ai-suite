#!/usr/bin/env python3
"""mitmproxy addon that records sanitized OpenCode endpoint observations."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from mitmproxy import http


OUTPUT_PATH = Path(os.environ.get("OPENCODE_PROBE_OUTPUT", "opencode-endpoints.jsonl"))


def write_observation(flow: http.HTTPFlow) -> None:
    """Write endpoint metadata without headers, credentials, or request bodies."""
    request = flow.request
    response = flow.response
    observation = {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": request.method,
        "scheme": request.scheme,
        "host": request.host,
        "port": request.port,
        "path": request.path,
        "url": request.url,
        "status_code": response.status_code if response else None,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("a", encoding="utf-8") as output_file:
        output_file.write(json.dumps(observation, sort_keys=True) + "\n")
    print(
        f"[opencode-endpoint-probe] {request.method} {request.url} "
        f"-> {response.status_code if response else 'no response'}",
        flush=True,
    )


class OpenCodeEndpointProbe:
    """Observe every decrypted HTTP request passing through mitmproxy."""

    def request(self, flow: http.HTTPFlow) -> None:
        """Attach request metadata; response adds the status code later."""
        flow.metadata["opencode_probe"] = True

    def response(self, flow: http.HTTPFlow) -> None:
        """Persist the completed request observation."""
        if flow.metadata.get("opencode_probe"):
            write_observation(flow)

    def error(self, flow: http.HTTPFlow) -> None:
        """Persist requests that fail before receiving an HTTP response."""
        if flow.metadata.get("opencode_probe"):
            write_observation(flow)


addons = [OpenCodeEndpointProbe()]

#!/usr/bin/env python3
"""Capture one Vercel gateway request body for a local curl replay."""

import json
from pathlib import Path

from mitmproxy import http


OUTPUT = Path("scratch/vercel-curl-request.json")


class CaptureVercelRequest:
    """Save the first gateway request body and non-secret headers."""

    def request(self, flow: http.HTTPFlow) -> None:
        if flow.request.host != "ai-gateway.vercel.sh":
            return
        if OUTPUT.exists():
            return
        body = flow.request.get_text(strict=False)
        try:
            parsed_body = json.loads(body)
        except json.JSONDecodeError:
            parsed_body = body
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(
                {
                    "method": flow.request.method,
                    "url": flow.request.url,
                    "headers": {
                        name: value
                        for name, value in flow.request.headers.items()
                        if name.lower() not in {"authorization", "cookie"}
                    },
                    "body": parsed_body,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


addons = [CaptureVercelRequest()]

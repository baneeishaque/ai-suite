# `probe-opencode-endpoints.py`

Run an OpenCode command through a local `mitmproxy` instance and discover the
actual HTTP endpoints OpenCode calls at runtime.

The probe writes JSON Lines to `scratch/opencode-endpoints.jsonl` by default.
Each record contains only the timestamp, method, scheme, host, port, path, URL,
and response status. It does not persist headers, authorization values, or
request/response bodies.

## Requirements

- Python 3.10+
- `mitmproxy` installed and `mitmdump` available on `PATH`
- OpenCode installed
- The mitmproxy CA trusted by Node, normally at
  `~/.mitmproxy/mitmproxy-ca-cert.pem`

Install mitmproxy in the active Python environment if needed:

```bash
python3 -m pip install mitmproxy
```

## Usage

Pass the OpenCode command after `--`; the probe forwards it unchanged:

```bash
python3 scripts/probe-opencode-endpoints.py -- \
  opencode run --model vercel/model "Reply with exactly: OK"
```

The probe starts `mitmdump` on `127.0.0.1:9453`, sets `HTTP_PROXY`,
`HTTPS_PROXY`, and their lowercase equivalents for the child process, and sets
`NODE_EXTRA_CA_CERTS` when the standard mitmproxy CA exists.

Use another port or output file when needed:

```bash
python3 scripts/probe-opencode-endpoints.py \
  --port 9454 \
  --output scratch/vercel-endpoints.jsonl \
  -- opencode run --model vercel/model "Reply with exactly: OK"
```

The command exits with OpenCode's exit code. A failed request is still useful:
the output can show the attempted host and path even when the response is an
HTTP error.

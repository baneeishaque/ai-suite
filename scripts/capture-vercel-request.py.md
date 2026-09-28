# `capture-vercel-request.py`

Mitmproxy addon for capturing one Vercel AI Gateway request in a form that can
be replayed with [`curl-vercel-symbol-prompt.sh`](curl-vercel-symbol-prompt.sh).

It writes the request URL, non-secret headers, and JSON body to
`scratch/vercel-curl-request.json`. `Authorization` and `Cookie` headers are
excluded.

```bash
mitmdump --listen-host 127.0.0.1 --listen-port 9454 \
  -s scripts/capture-vercel-request.py
```

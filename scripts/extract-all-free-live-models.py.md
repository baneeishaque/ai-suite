# Extract Free Live Models

`extract-all-free-live-models.py` reads the direct provider object from
OpenCode's `models.json` and the `provider` object from `opencode.json`, then
delegates each provider to the single-provider workflow. It writes one combined
provider file per provider whether authenticated or not.

Shared XDG path and JSON-loading behavior comes from
[`opencode_common.py`](opencode_common.py.md).
The wrapper also reuses its shared `load_provider_extractor()`,
`add_model_config_arguments()`, and `add_output_dir_argument()` helpers.

## Usage

With the standard OpenCode XDG directories:

```bash
python3 scripts/extract-all-free-live-models.py
```

This reads:

- `~/.cache/opencode/models.json`
- `~/.config/opencode/opencode.json`

Outputs are written to the current directory as
`provider-free-live-{provider}.json`. Each file contains the full merged provider
metadata with its `models` map restricted to free, live models.

For the private repository copy:

```bash
python3 scripts/extract-all-free-live-models.py \
  --models /Users/dk/lab-data/configurations-private/opencode/cache/models.json \
  --config /Users/dk/lab-data/configurations-private/opencode/config/opencode.json \
  --output-dir .
```

The script does not read, print, or require `auth.json`.

## Filtering

A model is included when:

- `cost.input` equals numeric `0`.
- `status` is absent or is not `deprecated`.

The script delegates the complete per-provider workflow to
`write_provider_file()` in `extract-provider-free-live-models.py`. Configured
model entries override cached entries with the same ID, while unique models
from both sources are preserved. The delegated function writes each file and
prints its model count. Providers with no free/live models produce no file and
are included in the skipped count.

Providers are collected from both model sources. Duplicate provider definitions
are merged, with configured model entries taking precedence for duplicate model
IDs and unique models from both sources preserved.

## Verification

```bash
python3 -m py_compile \
  scripts/opencode_common.py \
  scripts/extract-all-free-live-models.py
```

## Recommended Enhancements

- Add fixture-based tests for direct provider maps and model precedence.

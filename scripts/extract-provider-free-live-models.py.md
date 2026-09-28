# Extract Provider Free Live Models

`extract-provider-free-live-models.py` reads one provider from OpenCode's `models.json`
and `opencode.json`, applies configuration overrides, and writes one combined
provider file containing only free, live models.

The output is named `provider-free-live-{provider}.json`. It preserves provider
metadata such as `api`, `env`, and provider identifiers while replacing the
provider's `models` map with the filtered result.

`write_provider_file()` owns the complete merge, filter, filename, write, and
count-reporting workflow. It skips the output when no free/live models remain
and returns whether a file was written. The output filename is always
`provider-free-live-{provider}.json`. The all-provider wrapper reuses this
function for each provider.

Shared XDG path and JSON-loading behavior comes from
[`opencode_common.py`](opencode_common.py.md).
The shared `add_model_config_arguments()` and `add_output_dir_argument()`
helpers define the input and output directory options.

## Usage

```bash
python3 scripts/extract-provider-free-live-models.py kilo
```

The default inputs are `$XDG_CACHE_HOME/opencode/models.json` and
`$XDG_CONFIG_HOME/opencode/opencode.json`, falling back to
`~/.cache/opencode/models.json` and `~/.config/opencode/opencode.json`. Output
goes to the current directory by default.

For the private-repository setup used on this machine, OpenCode's native
`~/.cache/opencode/` path should resolve through the existing symlink:

```bash
python3 scripts/extract-provider-free-live-models.py kilo
```

If you need to read the repository copy directly, use the explicit path override:

```bash
python3 scripts/extract-provider-free-live-models.py kilo \
  --models /path/to/models.json \
  --config /path/to/opencode.json \
  --output-dir /path/to/output
```

## Processing Decisions

| Logic | Rationale |
| --- | --- |
| Provider lookup reads direct provider maps | Matches the current `models.json` and `opencode.json` schemas. |
| Configuration overrides duplicate provider fields | Local configuration takes precedence over cached metadata. |
| Configuration models override duplicate model IDs | Local definitions correct or extend cached definitions. |
| Input cost must equal numeric `0` | Excludes paid or incompletely described models. |
| Missing status is treated as live | Matches the original `(.status // "") != "deprecated"` filter. |
| One combined provider file is written | Keeps metadata and filtered models together for downstream consumers. |

## Edge Cases

- Missing files, malformed JSON, missing providers, or missing `models` objects
  exit with an error and status `1`.
- Models with non-object metadata are skipped rather than treated as valid model records.
- Existing output files are replaced deliberately on each run.

## Verification

```bash
python3 -m py_compile \
  scripts/opencode_common.py \
  scripts/extract-provider-free-live-models.py
```

## Recommended Enhancements

- Add fixture-based tests for configuration precedence and filtered provider output.

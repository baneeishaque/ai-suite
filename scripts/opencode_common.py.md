# OpenCode Common Helpers

`opencode_common.py` contains shared argument, filesystem, and JSON-loading
helpers used by the OpenCode scripts.
Keeping these operations in one module prevents the scripts from drifting apart in
how they resolve XDG paths or validate input files.

## Shared Type

```python
JsonObject = dict[str, Any]
```

`JsonObject` describes a JSON object with string keys. JSON values are typed as
`Any` because provider metadata can contain strings, numbers, booleans, arrays,
objects, or `null`.

## `xdg_path()`

```python
xdg_path(environment_name, fallback, *parts)
```

The helper:

1. Reads the requested XDG environment variable.
2. Uses the supplied fallback when the variable is absent.
3. Expands `~` with `Path.expanduser()`.
4. Appends the requested path components with `Path.joinpath()`.

For example, resolving `XDG_DATA_HOME` with `opencode/auth.json` produces:

```text
$XDG_DATA_HOME/opencode/auth.json
```

When `XDG_DATA_HOME` is unset, it falls back to:

```text
~/.local/share/opencode/auth.json
```

## Shared Argument Helpers

`add_model_config_arguments()` adds the common `--models` and `--config`
options to an `argparse` parser. Callers can provide custom defaults, which
allows Graphify to keep its private repository paths while sharing the option
definitions.

`add_output_dir_argument()` adds the common `--output-dir` option used by the
model extraction scripts and the Graphify generator. Callers can provide an
optional default directory and caller-specific help text. The Graphify
generator uses `~/.graphify` and writes `providers.json` inside that directory.

The helpers centralize option names, `Path` conversion, defaults, and help text.
Scripts retain their own `parse_arguments()` functions for unique options such as
the provider name and authentication path.

## Default OpenCode Paths

The three default-path helpers provide one canonical location for each OpenCode
file:

| Helper | Environment variable | Fallback | File |
| --- | --- | --- | --- |
| `default_auth_path()` | `XDG_DATA_HOME` | `~/.local/share` | `opencode/auth.json` |
| `default_models_path()` | `XDG_CACHE_HOME` | `~/.cache` | `opencode/models.json` |
| `default_config_path()` | `XDG_CONFIG_HOME` | `~/.config` | `opencode/opencode.json` |

The helpers return `Path` objects and do not create or modify files.

## `load_json_object()`

```python
load_json_object(path)
```

This helper loads a UTF-8 JSON file and validates that its top-level value is an
object.

It raises:

- `FileNotFoundError` when the path does not exist.
- `OSError` for other filesystem failures.
- `json.JSONDecodeError` for malformed JSON.
- `ValueError` when the JSON root is not an object.

The calling scripts catch these errors and convert them into a user-facing error
message with a non-zero exit status.

## `write_json()`

`write_json(path, value)` creates the parent directory when necessary and writes
an object as UTF-8 JSON with two-space indentation, ASCII escaping, and a
trailing newline. The provider extractor, all-provider extractor, and Graphify
generator use this same output format.

## Design Boundary

This module owns only shared infrastructure:

- XDG path resolution.
- OpenCode default paths.
- Top-level JSON loading and validation.
- Shared provider-extractor loading and environment-key selection.
- Common generated-output directory argument handling.

It does not own provider merging, authentication export, model filtering, or output
file generation. Those behaviors remain in their respective scripts.

## Consumers

- [export-opencode-auth-env.py](export-opencode-auth-env.py.md) uses the paths and
  loader to generate shell exports.
- [extract-all-free-live-models.py](extract-all-free-live-models.py.md)
  uses the same paths and loader to generate filtered model files.
- [generate-graphify-providers.py](generate-graphify-providers.py.md) uses the
  shared provider extractor, environment-key selector, and output-directory
  argument.

## Verification

```bash
python3 -m py_compile \
  scripts/opencode_common.py \
  scripts/export-opencode-auth-env.py \
  scripts/extract-all-free-live-models.py
```

## Recommended Enhancements

- Add unit tests for XDG overrides, fallback paths, missing files, malformed JSON,
  and non-object JSON roots.

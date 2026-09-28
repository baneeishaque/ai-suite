# Generate Graphify Providers

`generate-graphify-providers.py` builds
`~/.graphify/providers.json` from OpenCode's authenticated providers, cached
models, and configured model additions.

It reuses `merge_provider_data()` and `filter_free_live_models()` from
`extract-provider-free-live-models.py`, so all consumers apply the same
model precedence and free-live filtering rules.

## Usage

The defaults use the XDG OpenCode locations and write the registry beneath the
current user's home directory:

```bash
python3 scripts/generate-graphify-providers.py
```

Equivalent explicit invocation with custom paths:

```bash
python3 scripts/generate-graphify-providers.py \
  --auth /path/to/auth.json \
  --models /path/to/models.json \
  --config /path/to/opencode.json \
  --output-dir /path/to
```

The registry is always written as `providers.json` inside `--output-dir`.
The default output directory is `~/.graphify`, so the default output file is
`~/.graphify/providers.json`.

## Output Mapping

Each free-live OpenCode model becomes one flattened Graphify entry:

| Graphify field | OpenCode source |
| --- | --- |
| Entry key | Slugged provider name and model ID |
| `base_url` | Provider `api`, for `@ai-sdk/openai-compatible` providers |
| `default_model` | Model `id` |
| `env_key` | First explicit provider `env` entry |
| `pricing` | Model `cost.input` and `cost.output` |
| `temperature` | `0`, matching the existing Graphify registry format |

Configured provider models override cached models with the same ID. Unique
configured models are added.

Only providers whose merged metadata has `npm` set to
`@ai-sdk/openai-compatible` are eligible. Providers using another AI SDK
protocol, such as Vercel's `@ai-sdk/gateway`, are skipped even when a runtime
probe discovers a URL. Eligible providers must have an explicit non-empty
`api`, a non-empty key environment name, and a model `id`; the generator does
not infer any of these values from provider names or SDK defaults.
Provider iteration preserves the authentication file's order. The output
directory option is provided by `opencode_common.py` through
`add_output_dir_argument()`.

## Safety

The script reads authentication keys only to enumerate provider names. It never prints or copies credential values.

The output file is replaced on each run and is created along with its parent
directory when necessary.

## Verification

```bash
python3 -m py_compile \
  scripts/opencode_common.py \
  scripts/generate-graphify-providers.py
```

## Recommended Enhancements

- Add a `--dry-run` option that reports entry counts without replacing the registry.
- Add collision detection when multiple model IDs normalize to the same Graphify key.

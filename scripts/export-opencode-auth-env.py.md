# Export OpenCode Auth Environment

`export-opencode-auth-env.py` reads OpenCode `auth.json` and emits shell-safe
`export` statements for provider API keys. It is evaluated by the shared
`.zshenv`, so newly added auth providers are imported automatically.

Shared XDG path and JSON-loading behavior comes from
[`opencode_common.py`](opencode_common.py.md).
Environment-name validation and first-key selection also use its shared
`select_environment_key()` helper.

## Behavior

- Reads auth values from `$XDG_DATA_HOME/opencode/auth.json`, falling back to
  `~/.local/share/opencode/auth.json`.
- Reads models from `$XDG_CACHE_HOME/opencode/models.json`, falling back to
  `~/.cache/opencode/models.json`.
- Reads configured providers from `$XDG_CONFIG_HOME/opencode/opencode.json`,
  falling back to `~/.config/opencode/opencode.json`.
- Extracts only provider `env` lists from `models.json` and `opencode.json`;
  all other provider metadata is ignored.
- Merges both `env` lists by provider, preserving model names first and adding
  unique configuration names afterward.
- Uses `select_environment_key()` to accept only non-empty uppercase environment
  names ending in `_KEY`.
- Emits only the first matching environment name for each provider.
- Prints a warning to `stderr` when multiple matching names exist, including
  the selected and skipped environment names but never credential values.
- Emits the credential value as a shell export, so command substitution should
  be used only in a trusted shell configuration.

## Verification

```bash
python3 -m py_compile \
  scripts/opencode_common.py \
  scripts/export-opencode-auth-env.py
zsh -n /Users/dk/lab-data/configurations-private/Shell_Configurations/ZSH_Shell_Configurations/.zshenv
```

To inspect names without exposing values in the terminal:

```bash
python3 scripts/export-opencode-auth-env.py 2>&1 |
  sed -E 's/(export [A-Z0-9_]+)=.*/\1=<redacted>/'
```

## Recommended Enhancements

- Add focused unit tests for env-list merging, duplicate filtering, and
  multiple-key warnings.

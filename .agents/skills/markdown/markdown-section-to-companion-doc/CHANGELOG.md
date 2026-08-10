# Changelog — markdown-section-to-companion-doc

- 2026-08-10: Initial release (v1). Base primitive ships `scripts/split-section.py` with `--check` /
  `--split` / `--dry-run` modes, pointer-only idempotency, `###`-subheading containment, and exit-code
  contract (0 no-op / 1 inline-or-missing / 2 usage-IO). Consumed by the `skill-doc-metadata-separation`
  composer created in the same session (`01360e993ffeP65zXAhxHZ38wY`).

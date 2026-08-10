# Changelog — skill-doc-metadata-separation

- 2026-08-10: Initial release (v1). Composer ships `scripts/separate-skill-doc-metadata.py` with
  audit / dry-run / split lifecycle over single-skill or recursive-library targets, default section
  vocabulary (Changelog, Traceability), and base resolution anchored on its own location. Delegates
  all file mutation to the `markdown-section-to-companion-doc` base created in the same session
  (`01360e993ffeP65zXAhxHZ38wY`).

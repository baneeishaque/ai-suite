# Traceability — docker-resource-inventory

## Provenance

- Created: 2026-08-10
- Source: the "get rid of my docker resources" cleanup workflow — the
  inventory-first discipline (lesson L1) and the `docker system df` field
  contract were extracted from the live cleanup replay; `docker system df` uses
  `.TotalCount` (not `.Total`) in `--format` templates — verified empirically
  against Docker 29.4.0.
- Layer decision: per [`skill-factory` §2.0](../../skill-factory/SKILL.md)
  Layering Decision — the enumeration primitive is reusable across multiple
  future Docker workflows, so base/composer separation is MANDATORY.

## Validation Evidence

The full cleanup was replayed live (2026-08-10): inventory → scope gate →
`docker system prune -a --volumes` → stop-first correction → `docker rm` →
volume-prune survivor → final `docker system df` verification. The inventory
JSON shape and the `.TotalCount` template field were validated live against
Docker 29.4.0 on OrbStack.

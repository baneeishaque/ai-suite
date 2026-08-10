# Changelog — docker-resource-cleanup

## v1 (2026-08-10)

- Initial release — composer that cleans Docker resources (containers, images,
  volumes, build cache) with a mandatory base-inventory pre-flight, a human
  scope gate (`full` / `keep-running` / `unused`), stop-before-remove discipline,
  volume-prune survivor sweep, and post-cleanup verification; delegates all
  enumeration to `docker-resource-inventory`.

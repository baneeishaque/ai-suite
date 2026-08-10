# Changelog — docker-resource-inventory

## v1 (2026-08-10)

- Initial release — deterministic JSON + text inventory of Docker resources
  (containers running/stopped, images, volumes, `docker system df` with
  byte-precise `size_bytes` / `reclaimable_bytes`); exit-code contract
  (0/1/2/3); daemon-reachability gate before any enumeration; `.TotalCount`
  (not `.Total`) verified empirically against Docker 29.4.0.

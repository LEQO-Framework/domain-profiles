# LEQO Domain Profiles

Central repository of domain profiles for the LEQO low-code modeler. One
subdirectory per domain, one JSON file per profile revision.

## Structure

```
<domain>/
  <version>.json   # DomainProfile, matching the schema used by leqo-backend
                    # (app.model.domain_profile.DomainProfile) and
                    # leqo-evolution-engine (see openapi.yaml, DomainProfile schema)
index.json          # manifest listing all domains and their available versions
```

## Domain

Currently a single domain, **Finance**, evolved across eleven revisions
(`1.0.0` → `11.0.0`) rather than spread across many unrelated domains. Each
transition targets a different part of the conflict taxonomy: block removal,
type narrowing and widening, required and optional properties, `min`/`max`
constraints, constraint value changes and removals, block renames, custom
types, typed ports for data and control flow, and container blocks with a
restricted set of admissible children.

Revisions that have been superseded carry `"status": "deprecated"`. They stay
readable and can still be migrated away from, but a client should not offer
them for new models.

## Adding a domain or revision

1. Add/update `<domain>/<version>.json` (must match the `DomainProfile` schema:
   `name`, `version`, `domainBlocks` grouped by category).
2. Update `index.json` so the new domain/version is listed.

## Validation

`scripts/validate.py` checks that every `<domain>/<version>.json` matches the
`DomainProfile` schema and that `index.json` is consistent with the files on
disk (every listed version exists, every file is listed, `name`/`version`
match the manifest, `latest` is the highest version). It uses only the Python
standard library:

```bash
python scripts/validate.py
```

A GitHub Action (`.github/workflows/validate.yml`) runs this on every push and
pull request, so a malformed profile or an out-of-sync manifest fails CI.

## Consuming this repository

`index.json` lets a client discover the available domains and versions without
the GitHub API, and the profile files are then fetched directly over plain
HTTP, for example via raw.githubusercontent.com or from a local clone. No
server-side component is required, any static file host works.

A client points at the raw base URL of this repository, reads `index.json`,
and loads `<directory>/<version>.json` for the revisions it needs. In the LEQO
low-code modeler this is configured through `VITE_DOMAIN_PROFILES_URL`.

## License

Apache License 2.0, see [LICENSE](./LICENSE).

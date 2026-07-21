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

Currently a single domain, **Finance**, evolved across five revisions
(`1.0.0` → `5.0.0`) rather than spread across many unrelated domains — each
transition targets a different part of the conflict taxonomy (block removal,
type narrowing/widening, required/optional properties, `min`/`max`
constraints, constraint value changes and removals). See
[`leqo-evolution-use-cases`](https://github.com/stceri/leqo-evolution-use-cases)
for the corresponding models and the exact conflicts each transition
produces, including detection-engine gaps found along the way.

## Adding a domain or revision

1. Add/update `<domain>/<version>.json` (must match the `DomainProfile` schema:
   `name`, `version`, `domainBlocks` grouped by category).
2. Update `index.json` so the new domain/version is listed.

## Consuming this repository

`index.json` is meant to let a client discover available domains and versions
without needing the GitHub API, then fetch the individual profile files
directly (e.g. via raw.githubusercontent.com or a local clone).

**Status:** the LEQO modeler does not yet fetch profiles from this repository
automatically — today, domain profiles are created/imported manually via the
"Manage Domain Profiles" modal (`domainProfileModal.tsx`), which
exports/imports a different, flatter JSON shape (`{ name, nodes }`). Wiring
the modeler up to auto-load from here is a follow-up frontend task, not yet
implemented.

## License

Apache License 2.0, see [LICENSE](./LICENSE).

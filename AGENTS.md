# AGENTS.md

## Project Operating Rules

- Package manager: `uv` (Python 3.12). No `requirements.txt`. No Taskfile.
- Primary stack: Home Assistant custom integration, domain `evaplex`.
- Architecture: see `CONTEXT.md`.
- Public GitHub/HACS entry is `README.md`. Install as a HACS custom repository.
- Do not fork API contracts into this tree. Product contracts stay outside this repository.

<!-- AUTO-GENERATED: ENRICH-AGENTS -->
## Commands

| Task | Command |
| --- | --- |
| Install | `uv sync --group dev` |
| Lint | `uv run ruff check .` |
| Typecheck | `uv run mypy` |
| Tests | `uv run pytest` |
| Release notes | `uv run python scripts/release_notes.py --tag vX.Y.Z` |
| Publish release | Bump `version` in `custom_components/evaplex/manifest.json` and `pyproject.toml` to `X.Y.Z`; add a `## X.Y.Z` section to `CHANGELOG.md`; commit; push `main`; after CI: `git tag vX.Y.Z && git push origin vX.Y.Z` |

## Constraints

- This repository is public. Do not add live hosts, secrets, credentials, or request/response bodies to code, comments, docs, or tests.
- API base URL comes only from the config entry. Do not hardcode a production host.
- Do not log tokens, Authorization headers, or payload bodies.
- HTTP paths and headers live in `custom_components/evaplex/api/routes.py` only. Do not scatter copies.
- Feature → entity mapping lives in `custom_components/evaplex/application/feature_map.py` only.
- User-facing strings stay generic. Do not put server error codes in `strings.json`.
- Do not implement a device-setup UI. Do not duplicate product API documentation here.
- Keep a short English `README.md` at the repo root. Do not add `docs/`, a user wiki, or Add-to-HA badges.
- Files over 300 LOC are a defect. No `# noqa` / broad `type: ignore`.
- Releases are GitHub Releases on tag `vX.Y.Z` (manifest `version` is `X.Y.Z`). Do not force-retag. Do not invent a Taskfile. Historical tag `0.1.0` (no `v`) stays put.
- HACS Action must run without an `ignore` key. Do not add `ignore: brands` or any other ignore.
- Changelog and workflows stay public: no live hosts, tokens, or hub protocol essays.

## Relevant Skills

- `python-code-style` for lint and file-size discipline.
- `agentic-infrastructure` for these files.
<!-- END AUTO-GENERATED: ENRICH-AGENTS -->

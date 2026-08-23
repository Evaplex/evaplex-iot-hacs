# CONTEXT.md

Commands live in `AGENTS.md`. Human entry: `README.md`.

<!-- AUTO-GENERATED: ENRICH-CONTEXT -->
## Architecture Summary

Custom Home Assistant integration. Config flow asks for the Evaplex IoT Hub address first (empty field, no baked host), then PKCE sign-in. Entity set comes from the feature map, not from hardcoded device types.

## Repository Map

| Path | Responsibility |
| --- | --- |
| `custom_components/evaplex/__init__.py` | Setup / unload |
| `custom_components/evaplex/config_flow.py` | Sign-in flow |
| `custom_components/evaplex/coordinator.py` | 30s refresh |
| `custom_components/evaplex/application/feature_map.py` | Feature → HA entities |
| `custom_components/evaplex/application/refresh.py` | Snapshot assembly |
| `custom_components/evaplex/api/routes.py` | Paths and headers |
| `custom_components/evaplex/api/client.py` | Outbound HTTP |
| `custom_components/evaplex/api/parsers.py` | Response field reads |
| `custom_components/evaplex/{button,number,switch,sensor,binary_sensor}.py` | Platforms |
| `tests/` | Pytest without a live service |
| `scripts/release_notes.py` | Release notes from `CHANGELOG.md` or conventional commit subjects |
| `.github/workflows/` | hassfest, HACS, pytest, tagged GitHub Releases |

## Domain

- One config entry per Evaplex account.
- Devices already added in the Evaplex app.
- Unknown feature keys are skipped.

## Known gaps

- Not in Home Assistant core.
- Nabu Casa account linking is out of scope.
<!-- END AUTO-GENERATED: ENRICH-CONTEXT -->

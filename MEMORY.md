# MEMORY.md

- `2026-08-23`: Public tree. Do not log tokens, Authorization, or request/response bodies. API base URL is entered by the user; do not bake a production host. Device onboarding stays in the Evaplex app. Do not document the product API here.
- `2026-08-23`: Wizard step `user` is the hub URL (empty default) before OAuth/PKCE. Persist in config entry `data.api_base`. Do not restore `README.md`, `docs/`, or Add-to-HA badges. HACS `information` is ignored on purpose. Neutral invalid-TLD hosts stay in tests only.
- `2026-08-23`: Root `README.md` is required for public GitHub and the HACS card. Do not delete it. Still forbid Add-to-HA badges, `docs/` wiki, and baked API hosts. HACS `information` validation can run when the README exists; keep `render_readme` true.

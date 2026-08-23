# Changelog

Notable changes to the Evaplex Home Assistant integration.

## 0.1.2 - 2026-08-24

### Added

- Local brand images for the Home Assistant brands proxy (`icon.png` 256×256 and `icon@2x.png` 512×512). Same square mark is the logo fallback.

### Changed

- Renamed the public GitHub repository to `Evaplex/evaplex-iot-homeassistant`.

## 0.1.1 - 2026-08-24

### Changed

- Run the HACS Action without an `ignore` key so default-store validation can see a clean check.
- Grant GitHub Actions `contents: read` so checkout and HACS validation can reach the public repository.

## 0.1.0 - 2026-08-23

### Added

- Custom integration for Evaplex devices, installed through HACS as a custom repository.
- Setup wizard asks for the Evaplex IoT Hub address first (empty field, nothing prefilled), then sign-in.

### Documentation

- Public README for GitHub and the HACS card. No Add-to-HA badge and no baked API host.

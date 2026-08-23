# Evaplex

Home Assistant custom integration for Evaplex devices. Install it through [HACS](https://hacs.xyz) as a custom repository.

## Add the repository in HACS

1. Open HACS.
2. Open **Custom repositories**.
3. Add `https://github.com/Evaplex/evaplex-iot-homeassistant` and set the type to **Integration**.
4. Download **Evaplex**, then restart Home Assistant.

## Add the integration

1. Go to **Settings → Devices & services → Add integration** and choose **Evaplex**.
2. On the first wizard step, enter the address of your Evaplex IoT Hub. The field is empty on purpose — nothing is prefilled.
3. Copy the address from the Evaplex app or your account. Do not guess a hostname.
4. Sign in when prompted.

Devices already added in the Evaplex app appear after sign-in.

## License

MIT. See [LICENSE](LICENSE).

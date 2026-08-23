from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "evaplex"
MANUFACTURER = "Evaplex"

PLATFORMS: tuple[Platform, ...] = (
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
)

CONF_API_BASE = "api_base"
OAUTH_CLIENT_ID = "evaplex-ha"
OAUTH_SCOPES = "ha.devices.read ha.devices.control"

UPDATE_INTERVAL = timedelta(seconds=30)

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EvaplexApiClient, EvaplexApiError, EvaplexAuthError, EvaplexRateLimited
from .application import CoordinatorData, refresh_snapshots
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class EvaplexCoordinator(DataUpdateCoordinator[CoordinatorData]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: EvaplexApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            config_entry=entry,
        )
        self.client = client
        self._feature_cache: dict[str, tuple[int, tuple[str, ...]]] = {}

    async def _async_update_data(self) -> CoordinatorData:
        try:
            return await refresh_snapshots(self.client, self._feature_cache)
        except EvaplexAuthError as err:
            raise ConfigEntryAuthFailed from err
        except EvaplexRateLimited as err:
            raise UpdateFailed("rate limited") from err
        except EvaplexApiError as err:
            raise UpdateFailed("update failed") from err

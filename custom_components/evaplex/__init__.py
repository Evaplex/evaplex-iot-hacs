from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class EvaplexRuntimeData:
    client: Any
    coordinator: Any


async def async_setup_entry(hass: Any, entry: Any) -> bool:
    from homeassistant.exceptions import ConfigEntryNotReady
    from homeassistant.helpers import config_entry_oauth2_flow
    from homeassistant.helpers.config_entry_oauth2_flow import (
        ImplementationUnavailableError,
        OAuth2Session,
    )

    from .api import EvaplexApiClient, hub_url_from_entry
    from .config_flow import EvaplexOAuth2FlowHandler, EvaplexOAuth2Implementation
    from .const import CONF_API_BASE, PLATFORMS
    from .coordinator import EvaplexCoordinator

    api_base = hub_url_from_entry(entry.data, key=CONF_API_BASE)
    implementation = EvaplexOAuth2Implementation(hass, api_base)
    EvaplexOAuth2FlowHandler.async_register_implementation(hass, implementation)
    try:
        resolved = await config_entry_oauth2_flow.async_get_config_entry_implementation(hass, entry)
    except ImplementationUnavailableError as err:
        raise ConfigEntryNotReady from err

    session = OAuth2Session(hass, entry, resolved)
    client = EvaplexApiClient(session, api_base)
    coordinator = EvaplexCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = EvaplexRuntimeData(client=client, coordinator=coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: Any, entry: Any) -> bool:
    from .const import PLATFORMS

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: Any, entry: Any) -> None:
    await hass.config_entries.async_reload(entry.entry_id)

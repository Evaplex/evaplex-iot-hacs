from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import EvaplexApiError
from .application import HaPlatform, PlatformDecl
from .coordinator import EvaplexCoordinator
from .entity import EvaplexEntity, async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator

    def factory(device_id: str, decl: PlatformDecl) -> EvaplexPowerSwitch:
        return EvaplexPowerSwitch(coordinator, device_id, decl)

    async_setup_platform_entities(coordinator, entry, async_add_entities, HaPlatform.SWITCH, factory)


class EvaplexPowerSwitch(EvaplexEntity, SwitchEntity):
    def __init__(self, coordinator: EvaplexCoordinator, device_id: str, decl: PlatformDecl) -> None:
        super().__init__(coordinator, device_id, decl)
        self._force_off = False

    @property
    def is_on(self) -> bool | None:
        if self._force_off:
            return False
        snap = self.snapshot
        if snap is None:
            return None
        return snap.power_on

    def _handle_coordinator_update(self) -> None:
        self._force_off = False
        super()._handle_coordinator_update()

    async def async_turn_on(self, **kwargs: object) -> None:
        await self._async_set(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        await self._async_set(False)

    async def _async_set(self, on: bool) -> None:
        try:
            await self.coordinator.client.async_set_power(self._device_id, on)
        except EvaplexApiError:
            self._force_off = True
            self.async_write_ha_state()
            raise
        self._force_off = False
        await self.coordinator.async_request_refresh()

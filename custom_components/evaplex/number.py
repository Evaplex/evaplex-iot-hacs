from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api.client import clamp_portions
from .application import HaPlatform, PlatformDecl
from .application.feature_map import PORTIONS_MAX, PORTIONS_MIN
from .entity import EvaplexEntity, async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator

    def factory(device_id: str, decl: PlatformDecl) -> EvaplexPortionsNumber:
        return EvaplexPortionsNumber(coordinator, device_id, decl)

    async_setup_platform_entities(coordinator, entry, async_add_entities, HaPlatform.NUMBER, factory)


class EvaplexPortionsNumber(EvaplexEntity, NumberEntity):
    _attr_native_min_value = float(PORTIONS_MIN)
    _attr_native_max_value = float(PORTIONS_MAX)
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        snap = self.snapshot
        if snap is None or snap.default_portions is None:
            return None
        return float(snap.default_portions)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.async_set_portions(self._device_id, clamp_portions(value))
        await self.coordinator.async_request_refresh()

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .application import HaPlatform, PlatformDecl
from .entity import EvaplexEntity, async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator

    def factory(device_id: str, decl: PlatformDecl) -> EvaplexOnlineSensor:
        return EvaplexOnlineSensor(coordinator, device_id, decl)

    async_setup_platform_entities(
        coordinator, entry, async_add_entities, HaPlatform.BINARY_SENSOR, factory
    )


class EvaplexOnlineSensor(EvaplexEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def available(self) -> bool:
        return self.snapshot is not None

    @property
    def is_on(self) -> bool | None:
        snap = self.snapshot
        if snap is None:
            return None
        return snap.online

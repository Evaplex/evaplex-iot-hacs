from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .application import HaPlatform, PlatformDecl
from .application.feature_map import ENTITY_KCAL, ENTITY_NEXT_RUN, ENTITY_WEIGHT
from .coordinator import EvaplexCoordinator
from .entity import EvaplexEntity, async_setup_platform_entities


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator

    def factory(device_id: str, decl: PlatformDecl) -> EvaplexSensor:
        return EvaplexSensor(coordinator, device_id, decl)

    async_setup_platform_entities(coordinator, entry, async_add_entities, HaPlatform.SENSOR, factory)


class EvaplexSensor(EvaplexEntity, SensorEntity):
    def __init__(self, coordinator: EvaplexCoordinator, device_id: str, decl: PlatformDecl) -> None:
        super().__init__(coordinator, device_id, decl)
        if decl.entity_key == ENTITY_WEIGHT:
            self._attr_device_class = SensorDeviceClass.WEIGHT
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
        elif decl.entity_key == ENTITY_NEXT_RUN:
            self._attr_device_class = SensorDeviceClass.TIMESTAMP
        elif decl.entity_key == ENTITY_KCAL:
            self._attr_state_class = SensorStateClass.TOTAL
            self._attr_native_unit_of_measurement = "kcal"

    @property
    def native_value(self) -> float | datetime | None:
        snap = self.snapshot
        if snap is None:
            return None
        key = self._decl.entity_key
        if key == ENTITY_WEIGHT:
            return snap.weight_kg
        if key == ENTITY_NEXT_RUN:
            return snap.next_run_at
        if key == ENTITY_KCAL:
            return snap.kcal_today
        return None

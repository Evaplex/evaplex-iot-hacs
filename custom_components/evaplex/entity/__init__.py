from __future__ import annotations

from collections.abc import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..application import DeviceSnapshot, HaPlatform, PlatformDecl, decls_for_platform
from ..const import DOMAIN, MANUFACTURER
from ..coordinator import EvaplexCoordinator

EntityFactory = Callable[[str, PlatformDecl], CoordinatorEntity[EvaplexCoordinator]]


class EvaplexEntity(CoordinatorEntity[EvaplexCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EvaplexCoordinator,
        device_id: str,
        decl: PlatformDecl,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._decl = decl
        self._attr_unique_id = decl.unique_id(device_id)
        self._attr_translation_key = decl.entity_key

    @property
    def snapshot(self) -> DeviceSnapshot | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.devices.get(self._device_id)

    @property
    def available(self) -> bool:
        snap = self.snapshot
        return snap is not None and snap.online

    @property
    def device_info(self) -> DeviceInfo:
        snap = self.snapshot
        name = snap.display_name if snap else self._device_id
        model = snap.model if snap else None
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            manufacturer=MANUFACTURER,
            name=name,
            model=model,
        )


def async_setup_platform_entities(
    coordinator: EvaplexCoordinator,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    platform: HaPlatform,
    factory: EntityFactory,
) -> None:
    known: set[str] = set()

    def _discover() -> None:
        if coordinator.data is None:
            return
        created: list[CoordinatorEntity[EvaplexCoordinator]] = []
        for device in coordinator.data.devices.values():
            for decl in decls_for_platform(device.feature_keys, platform):
                uid = decl.unique_id(device.device_id)
                if uid in known:
                    continue
                known.add(uid)
                created.append(factory(device.device_id, decl))
        if created:
            async_add_entities(created)

    _discover()
    entry.async_on_unload(coordinator.async_add_listener(_discover))

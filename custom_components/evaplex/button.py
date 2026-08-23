from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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

    def factory(device_id: str, decl: PlatformDecl) -> EvaplexFeedButton:
        return EvaplexFeedButton(coordinator, device_id, decl)

    async_setup_platform_entities(coordinator, entry, async_add_entities, HaPlatform.BUTTON, factory)


class EvaplexFeedButton(EvaplexEntity, ButtonEntity):
    @property
    def available(self) -> bool:
        snap = self.snapshot
        return snap is not None and snap.online and not snap.busy

    async def async_press(self) -> None:
        snap = self.snapshot
        if snap is None:
            return
        portions = snap.default_portions if snap.default_portions is not None else 1
        await self.coordinator.client.async_feed(self._device_id, portions)
        await self.coordinator.async_request_refresh()

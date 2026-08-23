from __future__ import annotations

from typing import Any, Protocol

from ..api.parsers import (
    parse_feature_item,
    parse_feature_keys,
    parse_next_run_at,
    parse_portions_from_feature,
    parse_power_on,
    parse_schedule_hints,
)
from .feature_map import FEATURE_NUTRITION, FEATURE_POWER, FEATURE_WEIGHT, resolve_feature_keys
from .models import CoordinatorData, DeviceCard, DeviceSnapshot


class DeviceClient(Protocol):
    async def async_list_devices(self) -> list[DeviceCard]: ...

    async def async_device_features(self, device_id: str) -> dict[str, Any] | None: ...

    async def async_latest_weight(self, device_id: str) -> float | None: ...

    async def async_kcal_today(self, device_id: str) -> float | None: ...

    async def async_power_on(self, device_id: str) -> bool | None: ...


async def refresh_snapshots(
    client: DeviceClient,
    cache: dict[str, tuple[int, tuple[str, ...]]],
) -> CoordinatorData:
    cards = await client.async_list_devices()
    devices: dict[str, DeviceSnapshot] = {}
    for card in cards:
        payload, keys = await _resolve_features(client, card, cache)
        feeding = parse_feature_item(payload, "feeding")
        portions = card.default_portions
        if portions is None:
            portions = parse_portions_from_feature(feeding)
        power_on = parse_power_on(parse_feature_item(payload, FEATURE_POWER))
        if FEATURE_POWER in keys and power_on is None:
            power_on = await client.async_power_on(card.device_id)
        weight_kg = await client.async_latest_weight(card.device_id) if FEATURE_WEIGHT in keys else None
        kcal_today = await client.async_kcal_today(card.device_id) if FEATURE_NUTRITION in keys else None
        schedule = parse_feature_item(payload, "schedule")
        devices[card.device_id] = DeviceSnapshot(
            device_id=card.device_id,
            display_name=card.display_name,
            device_type=card.device_type,
            model=card.model,
            online=card.online,
            busy=card.busy,
            settings_version=card.settings_version,
            default_portions=portions,
            power_on=power_on,
            next_run_at=parse_next_run_at(schedule),
            weight_kg=weight_kg,
            kcal_today=kcal_today,
            feature_keys=keys,
            schedule_hints=parse_schedule_hints(schedule),
        )
    return CoordinatorData(devices)


async def _resolve_features(
    client: DeviceClient,
    card: DeviceCard,
    cache: dict[str, tuple[int, tuple[str, ...]]],
) -> tuple[dict[str, Any] | None, tuple[str, ...]]:
    cached = cache.get(card.device_id)
    payload = await client.async_device_features(card.device_id)
    manifest_keys = parse_feature_keys(payload)
    if manifest_keys is None and cached is not None and cached[0] == card.settings_version:
        return None, cached[1]
    keys = resolve_feature_keys(manifest_keys, card.capabilities)
    cache[card.device_id] = (card.settings_version, keys)
    return payload, keys

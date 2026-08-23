from __future__ import annotations

from typing import Any

import pytest
from custom_components.evaplex.application.models import DeviceCard
from custom_components.evaplex.application.refresh import refresh_snapshots

from tests.conftest import DEVICE_ID


class FakeClient:
    def __init__(
        self,
        cards: list[DeviceCard],
        features: dict[str, Any] | None,
        *,
        weight: float | None = None,
        kcal: float | None = None,
        power: bool | None = None,
    ) -> None:
        self.cards = cards
        self.features = features
        self.weight = weight
        self.kcal = kcal
        self.power = power
        self.feature_calls = 0

    async def async_list_devices(self) -> list[DeviceCard]:
        return self.cards

    async def async_device_features(self, device_id: str) -> dict[str, Any] | None:
        self.feature_calls += 1
        return self.features

    async def async_latest_weight(self, device_id: str) -> float | None:
        return self.weight

    async def async_kcal_today(self, device_id: str) -> float | None:
        return self.kcal

    async def async_power_on(self, device_id: str) -> bool | None:
        return self.power


def _card(*, capabilities: tuple[str, ...] = (), settings_version: int = 1) -> DeviceCard:
    return DeviceCard(
        device_id=DEVICE_ID,
        display_name="Feeder",
        device_type="pet_feeder",
        model="pet_feeder",
        online=True,
        busy=False,
        settings_version=settings_version,
        default_portions=2,
        capabilities=capabilities,
    )


@pytest.mark.asyncio
async def test_missing_features_falls_back_to_capabilities() -> None:
    client = FakeClient([_card(capabilities=("feed",))], None)

    data = await refresh_snapshots(client, {})

    snap = data.devices[DEVICE_ID]
    assert snap.feature_keys == ("feeding",)


@pytest.mark.asyncio
async def test_settings_version_change_refetches_features() -> None:
    cache: dict[str, tuple[int, tuple[str, ...]]] = {DEVICE_ID: (1, ("feeding",))}
    client = FakeClient(
        [_card(settings_version=2)],
        {"features": [{"key": "weight"}]},
        weight=3.1,
    )

    data = await refresh_snapshots(client, cache)

    assert client.feature_calls == 1
    assert data.devices[DEVICE_ID].feature_keys == ("weight",)
    assert data.devices[DEVICE_ID].weight_kg == 3.1
    assert cache[DEVICE_ID][0] == 2


@pytest.mark.asyncio
async def test_cached_keys_used_when_features_missing_and_version_same() -> None:
    cache: dict[str, tuple[int, tuple[str, ...]]] = {DEVICE_ID: (4, ("nutrition",))}
    client = FakeClient([_card(settings_version=4)], None, kcal=12.0)

    data = await refresh_snapshots(client, cache)

    assert data.devices[DEVICE_ID].feature_keys == ("nutrition",)
    assert data.devices[DEVICE_ID].kcal_today == 12.0

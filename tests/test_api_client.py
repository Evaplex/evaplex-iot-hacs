from __future__ import annotations

from typing import Any

import pytest
from custom_components.evaplex.api.client import EvaplexApiClient, async_account_profile, clamp_portions
from custom_components.evaplex.api.errors import EvaplexApiError, EvaplexAuthError, EvaplexRateLimited
from custom_components.evaplex.api.routes import (
    HEADER_IDEMPOTENCY,
    feature_action_path,
    feature_config_path,
    feature_data_path,
    settings_path,
)

from tests.conftest import API_BASE, DEVICE_ID


class FakeResponse:
    def __init__(
        self,
        status: int,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self.headers = headers or {}
        self._payload = payload or {}

    async def json(self, content_type: str | None = None) -> dict[str, Any]:
        return self._payload


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    async def async_request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append((method, url, kwargs))
        return self.response


@pytest.mark.asyncio
async def test_feed_sends_portions_and_idempotency_header() -> None:
    session = FakeSession(FakeResponse(200, {}))
    client = EvaplexApiClient(session, API_BASE)

    await client.async_feed(DEVICE_ID, 12)

    method, url, kwargs = session.calls[0]
    assert method == "post"
    assert url == f"{API_BASE}{feature_action_path(DEVICE_ID, 'feeding', 'feed')}"
    assert kwargs["json"]["params"]["portions"] == 10
    assert HEADER_IDEMPOTENCY in kwargs["headers"]


@pytest.mark.asyncio
async def test_set_portions_clamps_range() -> None:
    session = FakeSession(FakeResponse(200, {}))
    client = EvaplexApiClient(session, API_BASE)

    await client.async_set_portions(DEVICE_ID, 0)

    _, url, kwargs = session.calls[0]
    assert url == f"{API_BASE}{settings_path(DEVICE_ID)}"
    assert kwargs["json"] == {"default_portions": 1}


@pytest.mark.asyncio
async def test_set_power_sends_on_flag() -> None:
    session = FakeSession(FakeResponse(200, {}))
    client = EvaplexApiClient(session, API_BASE)

    await client.async_set_power(DEVICE_ID, True)

    _, url, kwargs = session.calls[0]
    assert url == f"{API_BASE}{feature_config_path(DEVICE_ID, 'power')}"
    assert kwargs["json"]["config"] == {"on": True}


@pytest.mark.asyncio
async def test_weight_uses_latest_entry() -> None:
    session = FakeSession(FakeResponse(200, {"entries": [{"payload": {"weight_g": 1500}}]}))
    client = EvaplexApiClient(session, API_BASE)

    value = await client.async_latest_weight(DEVICE_ID)

    assert value == 1.5
    _, url, kwargs = session.calls[0]
    assert url == f"{API_BASE}{feature_data_path(DEVICE_ID, 'weight')}"
    assert kwargs["params"] == {"limit": 1}


@pytest.mark.asyncio
async def test_kcal_requires_day_window() -> None:
    session = FakeSession(FakeResponse(200, {"buckets": []}))
    client = EvaplexApiClient(session, API_BASE)

    await client.async_kcal_today(DEVICE_ID)

    _, url, _ = session.calls[0]
    assert "from=" in url
    assert "to=" in url
    assert "bucket=day" in url


@pytest.mark.asyncio
async def test_auth_error_on_unauthorized() -> None:
    session = FakeSession(FakeResponse(401))
    client = EvaplexApiClient(session, API_BASE)

    with pytest.raises(EvaplexAuthError):
        await client.async_list_devices()


@pytest.mark.asyncio
async def test_rate_limit_reads_retry_after() -> None:
    session = FakeSession(FakeResponse(429, headers={"Retry-After": "7"}))
    client = EvaplexApiClient(session, API_BASE)

    with pytest.raises(EvaplexRateLimited) as err:
        await client.async_list_devices()
    assert err.value.retry_after == 7


class FakeWebSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response

    async def get(self, url: str, **kwargs: Any) -> FakeResponse:
        return self.response


@pytest.mark.asyncio
async def test_account_profile_rejects_missing_user() -> None:
    session = FakeWebSession(FakeResponse(200, {"display_name": "x"}))

    with pytest.raises(EvaplexApiError):
        await async_account_profile(session, API_BASE, "access")


def test_clamp_portions() -> None:
    assert clamp_portions(0) == 1
    assert clamp_portions(11) == 10
    assert clamp_portions(3) == 3

from __future__ import annotations

from typing import Any
from uuid import uuid4

from ..application.feature_map import PORTIONS_MAX, PORTIONS_MIN
from ..application.models import DeviceCard
from . import routes
from .errors import EvaplexApiError, EvaplexAuthError, EvaplexRateLimited, EvaplexUnavailable
from .parsers import (
    parse_account_id,
    parse_account_title,
    parse_device_cards,
    parse_kcal_today,
    parse_power_on,
    parse_weight_kg,
    utc_day_window,
)


class EvaplexApiClient:
    def __init__(self, session: Any, api_base: str) -> None:
        self._session = session
        self._api_base = api_base

    async def async_list_devices(self) -> list[DeviceCard]:
        payload = await self._json("get", routes.DEVICES)
        return parse_device_cards(payload)

    async def async_device_features(self, device_id: str) -> dict[str, Any] | None:
        try:
            return await self._json("get", routes.features_path(device_id))
        except EvaplexApiError as err:
            if err.status == 404:
                return None
            raise

    async def async_latest_weight(self, device_id: str) -> float | None:
        payload = await self._json(
            "get",
            routes.feature_data_path(device_id, "weight"),
            params={"limit": 1},
        )
        return parse_weight_kg(payload)

    async def async_kcal_today(self, device_id: str) -> float | None:
        start, end, today = utc_day_window()
        path = routes.feature_report_path(device_id, "nutrition", "summary")
        payload = await self._json("get", f"{path}?{routes.day_window_query(start, end)}")
        return parse_kcal_today(payload, today)

    async def async_power_on(self, device_id: str) -> bool | None:
        payload = await self._json("get", routes.feature_config_path(device_id, "power"))
        return parse_power_on(payload)

    async def async_feed(self, device_id: str, portions: int) -> None:
        await self._json(
            "post",
            routes.feature_action_path(device_id, "feeding", "feed"),
            json={"v": 1, "params": {"portions": clamp_portions(portions)}},
            headers={routes.HEADER_IDEMPOTENCY: str(uuid4())},
        )

    async def async_set_portions(self, device_id: str, portions: int) -> None:
        await self._json(
            "put",
            routes.settings_path(device_id),
            json={"default_portions": clamp_portions(portions)},
        )

    async def async_set_power(self, device_id: str, on: bool) -> None:
        await self._json(
            "put",
            routes.feature_config_path(device_id, "power"),
            json={"v": 1, "config": {"on": on}},
        )

    def _abs(self, path: str) -> str:
        return f"{self._api_base}{path}"

    async def _json(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        request_headers = {routes.HEADER_REQUEST_ID: str(uuid4())}
        if headers:
            request_headers.update(headers)
        response = await self._session.async_request(
            method,
            self._abs(path),
            json=json,
            params=params,
            headers=request_headers,
        )
        return await read_json(response)


async def async_account_profile(
    websession: Any,
    api_base: str,
    access_token: str,
) -> tuple[str, str]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        routes.HEADER_REQUEST_ID: str(uuid4()),
    }
    response = await websession.get(f"{api_base}{routes.ME}", headers=headers)
    payload = await read_json(response)
    try:
        return parse_account_id(payload), parse_account_title(payload)
    except ValueError as err:
        raise EvaplexApiError(response.status) from err


async def read_json(response: Any) -> dict[str, Any]:
    status = response.status
    if status == 401:
        raise EvaplexAuthError(status)
    if status == 429:
        retry_after = _retry_after(response)
        raise EvaplexRateLimited(status, retry_after)
    if 500 <= status <= 599:
        raise EvaplexUnavailable(status)
    if status >= 400:
        raise EvaplexApiError(status)
    payload = await response.json(content_type=None)
    return payload if isinstance(payload, dict) else {}


def clamp_portions(value: int | float) -> int:
    return max(PORTIONS_MIN, min(PORTIONS_MAX, int(value)))


def _retry_after(response: Any) -> int | None:
    raw = response.headers.get("Retry-After")
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None

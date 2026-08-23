from datetime import UTC, datetime, timedelta
from typing import Any

from ..application.models import DeviceCard


def parse_account_id(payload: dict[str, Any]) -> str:
    user_id = payload.get("user_id")
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("missing account")
    return user_id.strip()


def parse_account_title(payload: dict[str, Any]) -> str:
    name = payload.get("display_name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return "Evaplex"


def parse_device_cards(payload: dict[str, Any]) -> list[DeviceCard]:
    items = payload.get("devices")
    if not isinstance(items, list):
        return []
    cards: list[DeviceCard] = []
    for item in items:
        if isinstance(item, dict) and isinstance(item.get("device_id"), str):
            cards.append(parse_device_card(item))
    return cards


def parse_device_card(item: dict[str, Any]) -> DeviceCard:
    device_type = item["type"] if isinstance(item.get("type"), str) else "device"
    raw_name = item.get("display_name")
    if not isinstance(raw_name, str) or not raw_name.strip():
        raw_name = item.get("name") if isinstance(item.get("name"), str) else device_type
    model_id = item["model_id"] if isinstance(item.get("model_id"), str) else None
    capabilities = item.get("capabilities")
    return DeviceCard(
        device_id=item["device_id"],
        display_name=raw_name.strip() if isinstance(raw_name, str) else device_type,
        device_type=device_type,
        model=model_id or device_type,
        online=bool(item.get("online")),
        busy=bool(item.get("busy")),
        settings_version=_as_int(item.get("settings_version"), default=0),
        default_portions=parse_default_portions(item.get("settings")),
        capabilities=tuple(cap for cap in capabilities if isinstance(cap, str))
        if isinstance(capabilities, list)
        else (),
    )


def parse_default_portions(settings: Any) -> int | None:
    if not isinstance(settings, dict):
        return None
    feed = settings.get("feed")
    if isinstance(feed, dict):
        nested = feed.get("default_portions")
        if isinstance(nested, int) and not isinstance(nested, bool):
            return nested
    raw = settings.get("default_portions")
    if isinstance(raw, int) and not isinstance(raw, bool):
        return raw
    return None


def parse_feature_keys(payload: dict[str, Any] | None) -> list[str] | None:
    if payload is None:
        return None
    features = payload.get("features")
    if not isinstance(features, list):
        return []
    keys: list[str] = []
    for item in features:
        if isinstance(item, dict) and isinstance(item.get("key"), str):
            keys.append(item["key"])
    return keys


def parse_feature_item(payload: dict[str, Any] | None, key: str) -> dict[str, Any] | None:
    if payload is None:
        return None
    features = payload.get("features")
    if not isinstance(features, list):
        return None
    for item in features:
        if isinstance(item, dict) and item.get("key") == key:
            return item
    return None


def parse_next_run_at(feature: dict[str, Any] | None) -> datetime | None:
    state = _state(feature)
    raw = state.get("next_run_at") if state else None
    return parse_timestamp(raw) if isinstance(raw, str) else None


def parse_schedule_hints(feature: dict[str, Any] | None) -> tuple[str, ...]:
    state = _state(feature)
    hints = state.get("hints") if state else None
    if not isinstance(hints, list):
        return ()
    return tuple(item for item in hints if isinstance(item, str))


def parse_power_on(*sources: dict[str, Any] | None) -> bool | None:
    for source in sources:
        if not isinstance(source, dict):
            continue
        config = source.get("config")
        if not isinstance(config, dict):
            continue
        flag = config.get("on")
        if isinstance(flag, bool):
            return flag
    return None


def parse_portions_from_feature(feature: dict[str, Any] | None) -> int | None:
    if not isinstance(feature, dict):
        return None
    config = feature.get("config")
    if not isinstance(config, dict):
        return None
    raw = config.get("default_portions")
    if isinstance(raw, int) and not isinstance(raw, bool):
        return raw
    return None


def parse_weight_kg(payload: dict[str, Any]) -> float | None:
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return None
    first = entries[0]
    if not isinstance(first, dict):
        return None
    body = first.get("payload")
    if not isinstance(body, dict):
        return None
    grams = body.get("weight_g")
    if isinstance(grams, int | float):
        return float(grams) / 1000.0
    return None


def utc_day_window(now: datetime | None = None) -> tuple[str, str, str]:
    moment = now.astimezone(UTC) if now is not None else datetime.now(UTC)
    today = moment.date()
    return today.isoformat(), (today + timedelta(days=1)).isoformat(), today.isoformat()


def parse_kcal_today(payload: dict[str, Any], today: str) -> float | None:
    buckets = payload.get("buckets")
    if not isinstance(buckets, list):
        return None
    for bucket in buckets:
        if not isinstance(bucket, dict) or bucket.get("date") != today:
            continue
        kcal = bucket.get("kcal")
        if kcal is None:
            return None
        if isinstance(kcal, int | float):
            return float(kcal)
        return None
    return None


def parse_timestamp(raw: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _state(feature: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(feature, dict):
        return None
    state = feature.get("state")
    return state if isinstance(state, dict) else None


def _as_int(value: Any, *, default: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return default
    return value

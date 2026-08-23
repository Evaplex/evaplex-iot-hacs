from datetime import UTC, datetime

from custom_components.evaplex.api.parsers import (
    parse_account_id,
    parse_kcal_today,
    parse_next_run_at,
    parse_power_on,
    parse_schedule_hints,
    parse_weight_kg,
    utc_day_window,
)


def test_next_run_reads_state_field_not_hints() -> None:
    feature = {
        "state": {
            "next_run_at": "2026-08-23T10:00:00Z",
            "hints": ["schedule_paused"],
        }
    }
    parsed = parse_next_run_at(feature)
    assert parsed == datetime(2026, 8, 23, 10, 0, tzinfo=UTC)
    assert parse_schedule_hints(feature) == ("schedule_paused",)
    assert parse_next_run_at({"state": {"hints": ["2026-08-23T10:00:00Z"]}}) is None


def test_weight_converts_grams_to_kg() -> None:
    assert parse_weight_kg({"entries": [{"payload": {"weight_g": 4200}}]}) == 4.2
    assert parse_weight_kg({"entries": []}) is None


def test_kcal_uses_utc_day_bucket() -> None:
    now = datetime(2026, 8, 23, 22, 0, tzinfo=UTC)
    start, end, today = utc_day_window(now)
    assert start == "2026-08-23"
    assert end == "2026-08-24"
    assert today == "2026-08-23"
    payload = {
        "buckets": [
            {"date": "2026-08-22", "kcal": 10},
            {"date": "2026-08-23", "kcal": 171.0},
        ]
    }
    assert parse_kcal_today(payload, today) == 171.0
    assert parse_kcal_today({"buckets": [{"date": "2026-08-23", "kcal": None}]}, today) is None


def test_power_reads_on_flag() -> None:
    assert parse_power_on({"config": {"on": True}}) is True
    assert parse_power_on({"config": {}}) is None


def test_account_id_requires_value() -> None:
    assert parse_account_id({"user_id": "user-1"}) == "user-1"

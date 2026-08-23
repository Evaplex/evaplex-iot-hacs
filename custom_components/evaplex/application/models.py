from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class DeviceCard:
    device_id: str
    display_name: str
    device_type: str
    model: str
    online: bool
    busy: bool
    settings_version: int
    default_portions: int | None
    capabilities: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DeviceSnapshot:
    device_id: str
    display_name: str
    device_type: str
    model: str
    online: bool
    busy: bool
    settings_version: int
    default_portions: int | None
    power_on: bool | None
    next_run_at: datetime | None
    weight_kg: float | None
    kcal_today: float | None
    feature_keys: tuple[str, ...]
    schedule_hints: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CoordinatorData:
    devices: dict[str, DeviceSnapshot]

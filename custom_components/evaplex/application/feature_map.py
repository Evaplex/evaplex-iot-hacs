from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

PORTIONS_MIN = 1
PORTIONS_MAX = 10

FEATURE_FEEDING = "feeding"
FEATURE_POWER = "power"
FEATURE_WEIGHT = "weight"
FEATURE_SCHEDULE = "schedule"
FEATURE_NUTRITION = "nutrition"

FEATURE_KEYS: tuple[str, ...] = (
    FEATURE_FEEDING,
    FEATURE_NUTRITION,
    FEATURE_POWER,
    FEATURE_SCHEDULE,
    FEATURE_WEIGHT,
)

ENTITY_FEED = "feed"
ENTITY_PORTIONS = "default_portions"
ENTITY_POWER = "power"
ENTITY_WEIGHT = "weight"
ENTITY_NEXT_RUN = "next_run"
ENTITY_KCAL = "kcal_today"
ENTITY_ONLINE = "online"

CAPABILITY_FEED = "feed"
CAPABILITY_ON_OFF = "on_off"


class HaPlatform(StrEnum):
    BINARY_SENSOR = "binary_sensor"
    BUTTON = "button"
    NUMBER = "number"
    SENSOR = "sensor"
    SWITCH = "switch"


@dataclass(frozen=True, slots=True)
class PlatformDecl:
    platform: HaPlatform
    feature_key: str
    entity_key: str

    def unique_id(self, device_id: str) -> str:
        return unique_id_for(device_id, self.feature_key, self.entity_key)


ONLINE = PlatformDecl(HaPlatform.BINARY_SENSOR, "", ENTITY_ONLINE)

FEATURE_PLATFORMS: dict[str, tuple[PlatformDecl, ...]] = {
    FEATURE_FEEDING: (
        PlatformDecl(HaPlatform.BUTTON, FEATURE_FEEDING, ENTITY_FEED),
        PlatformDecl(HaPlatform.NUMBER, FEATURE_FEEDING, ENTITY_PORTIONS),
    ),
    FEATURE_POWER: (PlatformDecl(HaPlatform.SWITCH, FEATURE_POWER, ENTITY_POWER),),
    FEATURE_WEIGHT: (PlatformDecl(HaPlatform.SENSOR, FEATURE_WEIGHT, ENTITY_WEIGHT),),
    FEATURE_SCHEDULE: (PlatformDecl(HaPlatform.SENSOR, FEATURE_SCHEDULE, ENTITY_NEXT_RUN),),
    FEATURE_NUTRITION: (PlatformDecl(HaPlatform.SENSOR, FEATURE_NUTRITION, ENTITY_KCAL),),
}

CAPABILITY_FALLBACK: dict[str, tuple[str, ...]] = {
    CAPABILITY_FEED: (FEATURE_FEEDING,),
    CAPABILITY_ON_OFF: (FEATURE_POWER,),
}


def unique_id_for(device_id: str, feature_key: str, entity_key: str) -> str:
    if not feature_key:
        return f"{device_id}_{entity_key}"
    return f"{device_id}_{feature_key}_{entity_key}"


def resolve_feature_keys(
    manifest_keys: Iterable[str] | None,
    capabilities: Iterable[str],
) -> tuple[str, ...]:
    if manifest_keys is None or _is_empty(manifest_keys):
        return _from_capabilities(capabilities)
    known: list[str] = []
    seen: set[str] = set()
    for key in manifest_keys:
        if key not in FEATURE_PLATFORMS or key in seen:
            continue
        seen.add(key)
        known.append(key)
    return tuple(known)


def decls_for(feature_keys: Iterable[str]) -> tuple[PlatformDecl, ...]:
    decls: list[PlatformDecl] = [ONLINE]
    seen: set[str] = set()
    for key in feature_keys:
        mapping = FEATURE_PLATFORMS.get(key)
        if mapping is None:
            continue
        for decl in mapping:
            marker = decl.unique_id("__")
            if marker in seen:
                continue
            seen.add(marker)
            decls.append(decl)
    return tuple(decls)


def decls_for_platform(feature_keys: Iterable[str], platform: HaPlatform) -> tuple[PlatformDecl, ...]:
    return tuple(decl for decl in decls_for(feature_keys) if decl.platform == platform)


def _from_capabilities(capabilities: Iterable[str]) -> tuple[str, ...]:
    keys: list[str] = []
    seen: set[str] = set()
    for capability in capabilities:
        for key in CAPABILITY_FALLBACK.get(capability, ()):
            if key in seen:
                continue
            seen.add(key)
            keys.append(key)
    return tuple(keys)


def _is_empty(keys: Iterable[str]) -> bool:
    return next(iter(keys), None) is None

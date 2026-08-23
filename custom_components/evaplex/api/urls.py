from collections.abc import Mapping
from urllib.parse import urlparse


def hub_url_form_default() -> str:
    return ""


def normalize_api_base(raw: str) -> str:
    value = raw.strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("invalid api base")
    return value


def hub_url_from_entry(data: Mapping[str, object], key: str) -> str:
    raw = data.get(key)
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("invalid api base")
    return normalize_api_base(raw)

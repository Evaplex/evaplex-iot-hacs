from pathlib import Path

import pytest
from custom_components.evaplex.api.routes import AUTHORIZE, ME, TOKEN, authorize_url, token_url
from custom_components.evaplex.api.urls import hub_url_form_default, hub_url_from_entry, normalize_api_base

from tests.conftest import API_BASE

_FLOW = Path(__file__).resolve().parents[1] / "custom_components" / "evaplex" / "config_flow.py"


def test_user_step_default_is_empty() -> None:
    default = hub_url_form_default()
    assert default == ""
    assert "http" not in default
    assert "example.invalid" not in default
    flow = _FLOW.read_text(encoding="utf-8")
    assert "default=hub_url_form_default()" in flow
    assert "api.example.invalid" not in flow
    assert "https://" not in flow


def test_hub_url_and_oauth_urls_come_from_entry() -> None:
    data = {"api_base": f"{API_BASE}/"}
    base = hub_url_from_entry(data, key="api_base")
    assert base == API_BASE
    assert authorize_url(base) == f"{API_BASE}{AUTHORIZE}"
    assert token_url(base) == f"{API_BASE}{TOKEN}"
    assert f"{base}{ME}" == f"{API_BASE}{ME}"


def test_config_flow_asks_hub_url_before_oauth() -> None:
    flow = _FLOW.read_text(encoding="utf-8")
    user_at = flow.index("async def async_step_user")
    oauth_at = flow.index("return await self.async_step_auth()")
    assert user_at < oauth_at


@pytest.mark.parametrize(
    "raw",
    ["", " ", "not-a-url", "https://", "/relative", "ftp://hub.example.invalid"],
)
def test_hub_url_rejects_invalid_without_dns(raw: str) -> None:
    with pytest.raises(ValueError):
        hub_url_from_entry({"api_base": raw}, key="api_base")


def test_normalize_strips_slash_and_requires_scheme() -> None:
    assert normalize_api_base(f"{API_BASE}/") == API_BASE
    with pytest.raises(ValueError):
        normalize_api_base("not-a-url")
    with pytest.raises(ValueError):
        normalize_api_base("")


def test_authorize_and_token_are_under_api_base() -> None:
    assert authorize_url(API_BASE) == f"{API_BASE}{AUTHORIZE}"
    assert token_url(API_BASE) == f"{API_BASE}{TOKEN}"

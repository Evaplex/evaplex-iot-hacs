from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import SOURCE_REAUTH, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import async_account_profile, hub_url_form_default, hub_url_from_entry
from .api.errors import EvaplexApiError
from .api.routes import authorize_url, token_url
from .const import CONF_API_BASE, DOMAIN, OAUTH_CLIENT_ID, OAUTH_SCOPES

_LOGGER = logging.getLogger(__name__)

STEP_USER = vol.Schema({vol.Required(CONF_API_BASE, default=hub_url_form_default()): str})


class EvaplexOAuth2Implementation(config_entry_oauth2_flow.LocalOAuth2ImplementationWithPkce):
    def __init__(self, hass: HomeAssistant, api_base: str) -> None:
        super().__init__(
            hass,
            DOMAIN,
            OAUTH_CLIENT_ID,
            authorize_url=authorize_url(api_base),
            token_url=token_url(api_base),
        )

    @property
    def name(self) -> str:
        return "Evaplex"

    @property
    def extra_authorize_data(self) -> dict[str, str]:
        data = {"scope": OAUTH_SCOPES}
        data.update(super().extra_authorize_data)
        return data


class EvaplexOAuth2FlowHandler(config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN):
    DOMAIN = DOMAIN
    VERSION = 1

    def __init__(self) -> None:
        super().__init__()
        self._api_base: str | None = None

    @property
    def logger(self) -> logging.Logger:
        return _LOGGER

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._api_base = hub_url_from_entry(user_input, key=CONF_API_BASE)
            except ValueError:
                errors["base"] = "invalid_api_base"
            else:
                self._attach_implementation()
                return await self.async_step_auth()
        return self.async_show_form(step_id="user", data_schema=STEP_USER, errors=errors)

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        self._api_base = hub_url_from_entry(entry_data, key=CONF_API_BASE)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        self._attach_implementation()
        return await self.async_step_auth()

    async def async_oauth_create_entry(self, data: dict) -> ConfigFlowResult:
        if self._api_base is None:
            return self.async_abort(reason="cannot_connect")
        data[CONF_API_BASE] = self._api_base
        token = data.get("token", {})
        access_token = token.get("access_token") if isinstance(token, dict) else None
        if not isinstance(access_token, str) or not access_token:
            return self.async_abort(reason="oauth_error")
        try:
            account_id, title = await async_account_profile(
                async_get_clientsession(self.hass),
                self._api_base,
                access_token,
            )
        except EvaplexApiError:
            return self.async_abort(reason="cannot_connect")
        await self.async_set_unique_id(account_id)
        if self.source == SOURCE_REAUTH:
            return self.async_update_reload_and_abort(self._get_reauth_entry(), data_updates=data)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=title, data=data)

    def _attach_implementation(self) -> None:
        if self._api_base is None:
            raise RuntimeError("api base missing")
        implementation = EvaplexOAuth2Implementation(self.hass, self._api_base)
        self.async_register_implementation(self.hass, implementation)
        self.flow_impl = implementation

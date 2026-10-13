"""Config flow for the Frutafeia integration."""

from __future__ import annotations

import logging

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_SCAN_INTERVAL_HOURS,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
    MAX_SCAN_INTERVAL_HOURS,
    MIN_SCAN_INTERVAL_HOURS,
    TIMEOUT,
)
from .frutafeia_api import FrutafeiaAuthError, FrutafeiaClient, FrutafeiaError

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL_SELECTOR = NumberSelector(
    NumberSelectorConfig(
        min=MIN_SCAN_INTERVAL_HOURS,
        max=MAX_SCAN_INTERVAL_HOURS,
        step=1,
        unit_of_measurement="h",
    )
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): TextSelector(
            TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")
        ),
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD, autocomplete="current-password"
            )
        ),
        vol.Required(
            CONF_SCAN_INTERVAL_HOURS, default=DEFAULT_SCAN_INTERVAL_HOURS
        ): SCAN_INTERVAL_SELECTOR,
    }
)

STEP_REAUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD, autocomplete="current-password"
            )
        ),
    }
)


class FrutafeiaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Frutafeia."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str | int] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup."""
        errors: dict[str, str] = {}
        if user_input is not None:
            data, error = await self._validate(user_input)
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(str(data["socio"]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, str]
    ) -> ConfigFlowResult:
        """Handle re-authentication when the password has changed."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle the re-authentication confirmation step."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()
        username = reauth_entry.data[CONF_USERNAME]

        if user_input is not None:
            candidate = {
                CONF_USERNAME: username,
                CONF_PASSWORD: user_input[CONF_PASSWORD],
            }
            data, error = await self._validate(candidate)
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(str(data["socio"]))
                self._abort_if_unique_id_mismatch(reason="unique_id_mismatch")
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_PASSWORD: user_input[CONF_PASSWORD]},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_REAUTH_DATA_SCHEMA,
            errors=errors,
        )

    async def _validate(self, user_input: dict[str, str | int]) -> tuple[dict | None, str | None]:
        """Validate the credentials by performing a real login."""
        try:
            async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                client = FrutafeiaClient(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    session,
                )
                data = await client.async_get_data()
        except FrutafeiaAuthError:
            return None, "invalid_auth"
        except FrutafeiaError:
            return None, "cannot_connect"
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Unexpected error validating Frutafeia credentials")
            return None, "unknown"

        return {"socio": data.socio}, None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowWithReload:
        """Return the options flow for Frutafeia."""
        return FrutafeiaOptionsFlow()


class FrutafeiaOptionsFlow(OptionsFlowWithReload):
    """Handle the options flow for Frutafeia."""

    async def async_step_init(
        self, user_input: dict[str, int] | None = None
    ) -> ConfigFlowResult:
        """Handle the options flow."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        entry = self.config_entry
        current = entry.options.get(
            CONF_SCAN_INTERVAL_HOURS,
            entry.data.get(CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS),
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL_HOURS, default=current): SCAN_INTERVAL_SELECTOR
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

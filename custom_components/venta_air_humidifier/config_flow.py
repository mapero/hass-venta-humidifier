"""Config flow for Venta Air Humidifier integration."""
from __future__ import annotations

import logging
from typing import Any
import urllib3

from requests.exceptions import ConnectionError

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from venta_protocol_v3_device import Venta_Protocol_v3_Device

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )
    if len(data["host"]) < 3:
        raise InvalidHost

    d = Venta_Protocol_v3_Device(data["host"])
    await hass.async_add_executor_job(d.getStatus)
    if not d.MacAdress:
        raise InvalidHost

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": d.MacAdress}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Venta Air Humidifier."""

    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            pass

        return self.async_show_menu(
            step_id="user", menu_options=["discovery", "manual"]
        )

    async def async_step_manual(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except (ConnectionError, urllib3.exceptions.MaxRetryError):
                errors["base"] = "cannot_connect"
            except Exception as e:  # pylint: disable=broad-except
                errors["base"] = str(e)
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="manual", data_schema=DATA_SCHEMA, errors=errors
        )

    # async def async_step_user(
    #     self, user_input: dict[str, Any] | None = None
    # ) -> FlowResult:
    #     """Handle the initial step."""
    #     errors: dict[str, str] = {}
    #     if user_input is not None:
    #         try:
    #             info = await validate_input(self.hass, user_input)
    #         except CannotConnect:
    #             errors["base"] = "cannot_connect"
    #         except Exception:  # pylint: disable=broad-except
    #             _LOGGER.exception("Unexpected exception")
    #             errors["base"] = "unknown"
    #         else:
    #             return self.async_create_entry(title=info["title"], data=user_input)

    #     return self.async_show_form(
    #         step_id="user", data_schema=DATA_SCHEMA, errors=errors
    #     )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(HomeAssistantError):
    """Error to indicate there is invalid host."""

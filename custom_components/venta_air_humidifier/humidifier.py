"""
Platform for sensor integration.

This module defines a custom Home Assistant humidifier entity for Venta Air Humidifiers.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.humidifier import (
    SUPPORT_MODES,
    HumidifierEntity,
)

from venta_protocol_v3_device import Venta_Protocol_v3_Device


from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    MODE_NORMAL,
    DOMAIN,
    MODE_AUTO,
    MODE_BOOST,
    MODE_ECO,
    MODE_SLEEP,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up the Venta Air Humidifier platform.

    This function is called by Home Assistant when setting up the Venta Air Humidifier platform.
    It initializes the Venta_Protocol_v3_Device object and adds a VentaHumidifier
    entity to Home Assistant.
    """
    d = hass.data[DOMAIN][config_entry.entry_id]
    await hass.async_add_executor_job(d.getStatus)
    async_add_entities([VentaHumidifier(d)])


class VentaHumidifier(HumidifierEntity):
    """
    Venta Air Humidifier entity.

    This class defines a custom Home Assistant humidifier entity for Venta Air Humidifiers.
    """

    should_poll = True
    supported_features = SUPPORT_MODES

    def __init__(self, humidifier: Venta_Protocol_v3_Device) -> None:
        """
        Initialize the VentaHumidifier entity.

        This function initializes the VentaHumidifier entity with the given
        Venta_Protocol_v3_Device object.
        """
        self._humidifier = humidifier
        self._attr_unique_id = f"{self._humidifier.MacAdress}_humidifier"
        self._attr_name = f"Venta Humidifier {self._humidifier.MacAdress}"

    @property
    def current_humidity(self) -> int | None:
        """
        Return the current humidity level.

        This function returns the current humidity level reported by the Venta Air Humidifier.
        """
        return self._humidifier.Humidity

    @property
    def target_humidity(self) -> int | None:
        """
        Return the target humidity level.

        This function returns the target humidity level set on the Venta Air Humidifier.
        """
        return self._humidifier.TargetHum

    @property
    def is_on(self) -> bool | None:
        """
        Return whether the humidifier is on.

        This function returns whether the Venta Air Humidifier is currently turned on.
        """
        return self._humidifier.Power == 1

    @property
    def available_modes(self) -> list[str] | None:
        """
        Return the available modes.

        This function returns a list of available modes for the Venta Air Humidifier.
        """
        return [MODE_SLEEP, MODE_ECO, MODE_AUTO, MODE_BOOST, MODE_NORMAL]

    @property
    def mode(self) -> str | None:
        """
        Return the current mode.

        This function returns the current mode of the Venta Air Humidifier.
        """
        if self._humidifier.Automatic == 1:
            return MODE_AUTO
        if self._humidifier.SleepMode == 1:
            return MODE_SLEEP
        match self._humidifier.FanSpeed:
            case 1:
                return MODE_ECO
            case 2:
                return MODE_NORMAL
            case 3:
                return MODE_BOOST

    async def async_update(self):
        """
        Update the entity state.

        This function updates the state of the VentaHumidifier entity.
        """
        await self.hass.async_add_executor_job(self._humidifier.getStatus)

    async def async_set_humidity(self, humidity: int) -> None:
        """
        Set the target humidity level.

        This function sets the target humidity level on the Venta Air Humidifier.
        """
        await self.hass.async_add_executor_job(self._humidifier.setTargetHum, humidity)

    async def async_set_mode(self, mode: str) -> None:
        """
        Set the mode.

        This function sets the mode on the Venta Air Humidifier.
        """
        match mode:
            case "auto":
                await self.hass.async_add_executor_job(
                    self._humidifier.setAutomatic, True
                )
                return
            case "sleep":
                await self.hass.async_add_executor_job(
                    self._humidifier.setSleepMode, True
                )
                return
            case "eco":
                await self.hass.async_add_executor_job(self._humidifier.setFanSpeed, 1)
                return
            case "normal":
                await self.hass.async_add_executor_job(self._humidifier.setFanSpeed, 2)
                return
            case "boost":
                await self.hass.async_add_executor_job(self._humidifier.setFanSpeed, 3)
                return

    async def async_turn_off(self, **kwargs: Any) -> None:
        """
        Turn off the humidifier.

        This function turns off the Venta Air Humidifier.
        """
        await self.hass.async_add_executor_job(self._humidifier.setPower, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """
        Turn on the humidifier.

        This function turns on the Venta Air Humidifier.
        """
        await self.hass.async_add_executor_job(self._humidifier.setPower, True)

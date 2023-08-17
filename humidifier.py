"""Platform for sensor integration."""
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
    d = hass.data[DOMAIN][config_entry.entry_id]
    await hass.async_add_executor_job(d.getStatus)
    async_add_entities([VentaHumidifier(d)])


class VentaHumidifier(HumidifierEntity):
    should_poll = True
    supported_features = SUPPORT_MODES

    def __init__(self, humidifier: Venta_Protocol_v3_Device) -> None:
        self._humidifier = humidifier
        self._attr_unique_id = f"{self._humidifier.MacAdress}_humidifier"
        self._attr_name = f"Venta Humidifier {self._humidifier.MacAdress}"

    @property
    def current_humidity(self) -> int | None:
        return self._humidifier.Humidity

    @property
    def target_humidity(self) -> int | None:
        return self._humidifier.TargetHum

    @property
    def is_on(self) -> bool | None:
        return self._humidifier.Power == 1

    @property
    def available_modes(self) -> list[str] | None:
        return [MODE_SLEEP, MODE_ECO, MODE_AUTO, MODE_BOOST, MODE_NORMAL]

    @property
    def mode(self) -> str | None:
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
        await self.hass.async_add_executor_job(self._humidifier.getStatus)

    async def async_set_humidity(self, humidity: int) -> None:
        await self.hass.async_add_executor_job(self._humidifier.setTargetHum, humidity)

    async def async_set_mode(self, mode: str) -> None:
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
        await self.hass.async_add_executor_job(self._humidifier.setPower, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(self._humidifier.setPower, True)

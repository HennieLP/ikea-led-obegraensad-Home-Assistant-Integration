"""Switch platform for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.ikea_obegraensad.const import DOMAIN
from custom_components.ikea_obegraensad.coordinator import IkeaLedCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IKEA OBEGRÄNSAD LED switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    switches = [
        IkeaLedScheduleSwitch(coordinator, entry),
    ]
    
    async_add_entities(switches)


class IkeaLedScheduleSwitch(CoordinatorEntity[IkeaLedCoordinator], SwitchEntity):
    """Switch for controlling schedule status."""

    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the schedule switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_schedule_switch"
        self._attr_name = "IKEA OBEGRÄNSAD Schedule"
        self._attr_icon = "mdi:calendar-clock"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="IKEA OBEGRÄNSAD LED",
            manufacturer="IKEA (Modified)",
            model="OBEGRÄNSAD",
            configuration_url=f"http://{self.coordinator.host}",
        )

    @property
    def is_on(self) -> bool:
        """Return true if schedule is active."""
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("scheduleActive", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return None
            
        return {
            "schedule": self.coordinator.data.get("schedule", [])
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the schedule."""
        await self.hass.async_add_executor_job(
            self.coordinator.set_schedule_state, True
        )
        
        # Gentle refresh to ensure UI updates
        await self.coordinator.async_refresh_after_command()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the schedule."""
        await self.hass.async_add_executor_job(
            self.coordinator.set_schedule_state, False
        )
        
        # Gentle refresh to ensure UI updates
        await self.coordinator.async_refresh_after_command()

"""Switch platform for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import IkeaLedCoordinator
from .entity import IkeaLedEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IKEA OBEGRÄNSAD LED switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IkeaLedScheduleSwitch(coordinator, entry)])


class IkeaLedScheduleSwitch(IkeaLedEntity, SwitchEntity):
    """Switch that starts and stops the schedule stored on the device."""

    _attr_name = "IKEA OBEGRÄNSAD Schedule"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the schedule switch."""
        super().__init__(coordinator, entry, "schedule_switch")

    @property
    def is_on(self) -> bool:
        """Return true if the schedule is running."""
        return bool((self.coordinator.data or {}).get("scheduleActive", False))

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the schedule entries."""
        data = self.coordinator.data
        if not data:
            return None
        return {"schedule": data.get("schedule", [])}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start the schedule."""
        await self.coordinator.async_set_schedule_active(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop the schedule."""
        await self.coordinator.async_set_schedule_active(False)

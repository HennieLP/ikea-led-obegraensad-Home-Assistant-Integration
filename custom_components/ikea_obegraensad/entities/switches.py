"""Switch entities for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging
from functools import cached_property
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry

from ..coordinator import IkeaLedCoordinator
from ..entities.base import IkeaLedBaseEntity

_LOGGER = logging.getLogger(__name__)


class IkeaLedSwitchBase(IkeaLedBaseEntity, SwitchEntity):
    """Base class for IKEA OBEGRÄNSAD LED switches."""
    
    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
        switch_key: str,
        name: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, entry, "switch", name, icon, switch_key)


class IkeaLedScheduleSwitch(IkeaLedSwitchBase):
    """Switch for controlling schedule status."""

    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the schedule switch."""
        super().__init__(
            coordinator,
            entry,
            "schedule",
            "Schedule",
            "mdi:calendar-clock"
        )

    @cached_property
    def is_on(self) -> bool:
        """Return true if schedule is active."""
        return self.get_data_value("scheduleActive", False)

    @cached_property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if not self.data:
            return None
            
        return {
            "schedule": self.get_data_value("schedule", [])
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the schedule."""
        await self.execute_command(self.coordinator.set_schedule_state, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the schedule."""
        await self.execute_command(self.coordinator.set_schedule_state, False)
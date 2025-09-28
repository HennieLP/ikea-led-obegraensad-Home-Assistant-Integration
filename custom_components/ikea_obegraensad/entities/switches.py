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


class PowerSwitch(IkeaLedSwitchBase):
    """Switch for power control."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the power switch."""
        super().__init__(coordinator, entry, "power_switch", "Power", "mdi:power")

    @cached_property  # type: ignore[misc]
    def is_on(self) -> bool:
        """Return true if the light is on."""
        return self.get_data_value("brightness", 0) > 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        await self.execute_command(self.coordinator.set_brightness, 255)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.execute_command(self.coordinator.set_brightness, 0)


class EffectSwitch(IkeaLedSwitchBase):
    """Switch for effect mode."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the effect switch."""
        super().__init__(coordinator, entry, "effect_switch", "Effect Mode", "mdi:auto-fix")

    @cached_property  # type: ignore[misc]
    def is_on(self) -> bool:
        """Return true if effects are enabled."""
        return False  # Placeholder

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable effects."""
        _LOGGER.info("Effect mode enable not yet implemented")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable effects."""
        _LOGGER.info("Effect mode disable not yet implemented")


class AutoBrightnessSwitch(IkeaLedSwitchBase):
    """Switch for auto brightness."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the auto brightness switch."""
        super().__init__(coordinator, entry, "auto_brightness_switch", "Auto Brightness", "mdi:brightness-auto")

    @cached_property  # type: ignore[misc]
    def is_on(self) -> bool:
        """Return true if auto brightness is enabled."""
        return False  # Placeholder

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable auto brightness."""
        _LOGGER.info("Auto brightness enable not yet implemented")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable auto brightness."""
        _LOGGER.info("Auto brightness disable not yet implemented")


__all__ = [
    "IkeaLedSwitchBase",
    "IkeaLedScheduleSwitch",
    "PowerSwitch",
    "EffectSwitch",
    "AutoBrightnessSwitch",
]
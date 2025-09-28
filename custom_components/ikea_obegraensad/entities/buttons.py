"""Button entities for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry

from ..coordinator import IkeaLedCoordinator
from ..entities.base import IkeaLedBaseEntity

_LOGGER = logging.getLogger(__name__)


class IkeaLedButtonBase(IkeaLedBaseEntity, ButtonEntity):
    """Base class for IKEA OBEGRÄNSAD LED buttons."""
    
    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
        button_key: str,
        name: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry, "button", name, icon, button_key)


class IkeaLedRotateLeftButton(IkeaLedButtonBase):
    """Button to rotate display left."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the rotate left button."""
        super().__init__(
            coordinator,
            entry,
            "rotate_left",
            "Rotate Left",
            "mdi:rotate-left"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.execute_command(self.coordinator.set_rotation, "left")


class IkeaLedRotateRightButton(IkeaLedButtonBase):
    """Button to rotate display right."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the rotate right button."""
        super().__init__(
            coordinator,
            entry,
            "rotate_right",
            "Rotate Right",
            "mdi:rotate-right"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.execute_command(self.coordinator.set_rotation, "right")


class IkeaLedRebootButton(IkeaLedButtonBase):
    """Button to reboot the device."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the reboot button."""
        super().__init__(
            coordinator,
            entry,
            "reboot",
            "Reboot",
            "mdi:restart"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        # Note: This would need to be implemented in the coordinator
        # await self.execute_command(self.coordinator.reboot_device)
        _LOGGER.warning("Reboot functionality not yet implemented")


# Aliases for registry compatibility
RestartButton = IkeaLedRebootButton


class ResetButton(IkeaLedButtonBase):
    """Button to reset device to defaults."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the reset button."""
        super().__init__(
            coordinator,
            entry,
            "reset",
            "Reset to Default",
            "mdi:backup-restore"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.warning("Reset functionality not yet implemented")


class PowerToggleButton(IkeaLedButtonBase):
    """Button to toggle power."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the power toggle button."""
        super().__init__(
            coordinator,
            entry,
            "power_toggle",
            "Power Toggle",
            "mdi:power"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        if self.coordinator.data and self.coordinator.data.get("brightness", 0) > 0:
            await self.execute_command(self.coordinator.set_brightness, 0)
        else:
            await self.execute_command(self.coordinator.set_brightness, 255)


class BrightnessDownButton(IkeaLedButtonBase):
    """Button to decrease brightness."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the brightness down button."""
        super().__init__(
            coordinator,
            entry,
            "brightness_down",
            "Brightness Down",
            "mdi:brightness-4"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        if self.coordinator.data:
            current_brightness = self.coordinator.data.get("brightness", 50)
            new_brightness = max(0, current_brightness - 10)
            await self.execute_command(self.coordinator.set_brightness, new_brightness)


class BrightnessUpButton(IkeaLedButtonBase):
    """Button to increase brightness."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the brightness up button."""
        super().__init__(
            coordinator,
            entry,
            "brightness_up",
            "Brightness Up",
            "mdi:brightness-7"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        if self.coordinator.data:
            current_brightness = self.coordinator.data.get("brightness", 50)
            new_brightness = min(255, current_brightness + 10)
            await self.execute_command(self.coordinator.set_brightness, new_brightness)


__all__ = [
    "IkeaLedButtonBase",
    "IkeaLedRotateLeftButton",
    "IkeaLedRotateRightButton", 
    "IkeaLedRebootButton",
    "RestartButton",
    "ResetButton",
    "PowerToggleButton",
    "BrightnessDownButton",
    "BrightnessUpButton",
]
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
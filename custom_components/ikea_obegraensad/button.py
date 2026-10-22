"""Button platform for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    """Set up the IKEA OBEGRÄNSAD LED button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IkeaLedRotateButton(coordinator, entry)])


class IkeaLedRotateButton(IkeaLedEntity, ButtonEntity):
    """Button to rotate the display by 90 degrees."""

    _attr_name = "IKEA OBEGRÄNSAD Rotate 90°"
    _attr_icon = "mdi:rotate-right"

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the rotate button."""
        super().__init__(coordinator, entry, "rotate")

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_rotate("right")

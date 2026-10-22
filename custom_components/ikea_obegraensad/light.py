"""Light platform for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
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
    """Set up the IKEA OBEGRÄNSAD LED light platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IkeaLedLight(coordinator, entry)])


class IkeaLedLight(IkeaLedEntity, LightEntity):
    """Representation of an IKEA OBEGRÄNSAD LED light."""

    _attr_name = "IKEA OBEGRÄNSAD LED"
    _attr_icon = "mdi:led-strip"
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the light."""
        super().__init__(coordinator, entry, "light")

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return (self.coordinator.data or {}).get("brightness", 0) > 0

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return (self.coordinator.data or {}).get("brightness")

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        data = self.coordinator.data
        if not data:
            return None
        return {
            "plugin": data.get("plugin"),
            "rotation": data.get("rotation"),
            "schedule_active": data.get("scheduleActive", False),
            "available_plugins": [
                f"{plugin.get('id')}: {plugin.get('name', 'Unknown')}"
                for plugin in data.get("plugins", [])
            ],
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        await self.coordinator.async_set_brightness(kwargs.get(ATTR_BRIGHTNESS, 255))

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.coordinator.async_set_brightness(0)

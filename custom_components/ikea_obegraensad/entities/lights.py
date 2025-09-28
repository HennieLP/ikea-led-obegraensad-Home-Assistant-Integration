"""Light entities for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging
from functools import cached_property
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry

from ..coordinator import IkeaLedCoordinator
from ..entities.base import IkeaLedBaseEntity

_LOGGER = logging.getLogger(__name__)


class IkeaLedLight(IkeaLedBaseEntity, LightEntity):
    """Representation of an IKEA OBEGRÄNSAD LED light."""

    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator, entry, "light", "LED", "mdi:led-strip")
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_features = LightEntityFeature.TRANSITION

    @cached_property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.get_data_value("brightness", 0) > 0

    @cached_property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self.get_data_value("brightness", 0)

    @cached_property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if not self.data:
            return None
            
        return {
            "plugin": self.get_data_value("plugin"),
            "rotation": self.get_data_value("rotation"),
            "available_plugins": [
                f"{plugin.get('id')}: {plugin.get('name', 'Unknown')}"
                for plugin in self.get_data_value("plugins", [])
            ],
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        await self.execute_command(self.coordinator.set_brightness, brightness)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.execute_command(self.coordinator.set_brightness, 0)
"""Light platform for IKEA OBEGRÄNSAD LED Control."""
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
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import IkeaLedCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IKEA OBEGRÄNSAD LED light platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([IkeaLedLight(coordinator, entry)])


class IkeaLedLight(CoordinatorEntity[IkeaLedCoordinator], LightEntity):  # type: ignore[misc]
    """Representation of an IKEA OBEGRÄNSAD LED light."""

    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_light"
        self._attr_name = "IKEA OBEGRÄNSAD LED"
        self._attr_icon = "mdi:led-strip"
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_features = LightEntityFeature.TRANSITION

    @cached_property  # type: ignore[misc]
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="IKEA OBEGRÄNSAD LED",
            manufacturer="IKEA (Modified)",
            model="OBEGRÄNSAD",
            configuration_url=f"http://{self.coordinator.host}",
        )

    @cached_property  # type: ignore[misc]
    def is_on(self) -> bool:
        """Return true if light is on."""
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("brightness", 0) > 0

    @cached_property  # type: ignore[misc]
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("brightness", 0)

    @cached_property  # type: ignore[misc]
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return None
            
        return {
            "plugin": self.coordinator.data.get("plugin"),
            "rotation": self.coordinator.data.get("rotation"),
            "schedule_active": self.coordinator.data.get("scheduleActive", False),
            "available_plugins": [
                f"{plugin.get('id')}: {plugin.get('name', 'Unknown')}"
                for plugin in self.coordinator.data.get("plugins", [])
            ],
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        try:
            brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
            await self.hass.async_add_executor_job(
                self.coordinator.set_brightness, brightness
            )
            # Gentle refresh to ensure UI updates
            await self.coordinator.async_refresh_after_command()
        except Exception as ex:
            _LOGGER.error("Failed to turn on light: %s", ex)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.set_brightness, 0
            )
            # Gentle refresh to ensure UI updates
            await self.coordinator.async_refresh_after_command()
        except Exception as ex:
            _LOGGER.error("Failed to turn off light: %s", ex)

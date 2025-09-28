"""Select entities for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging
from functools import cached_property
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry

from ..coordinator import IkeaLedCoordinator
from ..entities.base import IkeaLedBaseEntity

_LOGGER = logging.getLogger(__name__)


class IkeaLedSelectBase(IkeaLedBaseEntity, SelectEntity):
    """Base class for IKEA OBEGRÄNSAD LED selects."""
    
    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
        select_key: str,
        name: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, entry, "select", name, icon, select_key)


class IkeaLedPluginSelect(IkeaLedSelectBase):
    """Representation of an IKEA OBEGRÄNSAD LED plugin selector."""

    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(
            coordinator,
            entry,
            "plugin",
            "Plugin",
            "mdi:format-list-bulleted"
        )

    @cached_property
    def options(self) -> list[str]:
        """Return a list of selectable options."""
        plugins = self.get_data_value("plugins", [])
        return [
            f"{plugin.get('id')}: {plugin.get('name', 'Unknown')}"
            for plugin in plugins
        ]

    @cached_property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        current_plugin_id = self.get_data_value("plugin")
        if current_plugin_id is None:
            return None
            
        # Find the matching plugin name
        plugins = self.get_data_value("plugins", [])
        for plugin in plugins:
            if plugin.get("id") == current_plugin_id:
                return f"{plugin.get('id')}: {plugin.get('name', 'Unknown')}"
                
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            plugin_id = int(option.split(":")[0].strip())
            await self.execute_command(self.coordinator.set_plugin, plugin_id)
        except (ValueError, IndexError):
            _LOGGER.error("Failed to parse plugin ID from option: %s", option)
            raise


class BrightnessSelect(IkeaLedSelectBase):
    """Select for brightness level."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the brightness select."""
        super().__init__(coordinator, entry, "brightness_select", "Brightness Level", "mdi:brightness-6")
        self._attr_options = ["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]

    @cached_property  # type: ignore[misc]
    def current_option(self) -> str | None:
        """Return current brightness as percentage."""
        brightness = self.get_data_value("brightness", 0)
        return f"{int(brightness * 100 / 255)}%" if brightness is not None else None

    async def async_select_option(self, option: str) -> None:
        """Set brightness from percentage."""
        try:
            percentage = int(option.rstrip("%"))
            brightness = int(percentage * 255 / 100)
            await self.execute_command(self.coordinator.set_brightness, brightness)
        except (ValueError, TypeError):
            _LOGGER.error("Failed to parse brightness from option: %s", option)
            raise


class ColorSelect(IkeaLedSelectBase):
    """Select for color presets."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the color select."""
        super().__init__(coordinator, entry, "color_select", "Color Preset", "mdi:palette")
        self._attr_options = ["Red", "Green", "Blue", "White", "Yellow", "Cyan", "Magenta", "Orange"]

    @cached_property  # type: ignore[misc]
    def current_option(self) -> str | None:
        """Return current color."""
        # This would need to be implemented based on actual color data
        return "White"  # Placeholder

    async def async_select_option(self, option: str) -> None:
        """Set color preset."""
        _LOGGER.info("Color preset selection not yet implemented: %s", option)


class ColorModeSelect(IkeaLedSelectBase):
    """Select for color mode."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the color mode select."""
        super().__init__(coordinator, entry, "color_mode_select", "Color Mode", "mdi:palette-advanced")
        self._attr_options = ["Single", "Rainbow", "Fade", "Strobe"]

    @cached_property  # type: ignore[misc]
    def current_option(self) -> str | None:
        """Return current color mode."""
        return "Single"  # Placeholder

    async def async_select_option(self, option: str) -> None:
        """Set color mode."""
        _LOGGER.info("Color mode selection not yet implemented: %s", option)


class EffectSelect(IkeaLedSelectBase):
    """Select for effects."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the effect select."""
        super().__init__(coordinator, entry, "effect_select", "Effect", "mdi:auto-fix")
        self._attr_options = ["None", "Fade", "Strobe", "Rainbow", "Color Cycle"]

    @cached_property  # type: ignore[misc]
    def current_option(self) -> str | None:
        """Return current effect."""
        return "None"  # Placeholder

    async def async_select_option(self, option: str) -> None:
        """Set effect."""
        _LOGGER.info("Effect selection not yet implemented: %s", option)


class SpeedSelect(IkeaLedSelectBase):
    """Select for effect speed."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the speed select."""
        super().__init__(coordinator, entry, "speed_select", "Effect Speed", "mdi:speedometer")
        self._attr_options = ["Slow", "Medium", "Fast"]

    @cached_property  # type: ignore[misc]
    def current_option(self) -> str | None:
        """Return current speed."""
        return "Medium"  # Placeholder

    async def async_select_option(self, option: str) -> None:
        """Set effect speed."""
        _LOGGER.info("Speed selection not yet implemented: %s", option)


__all__ = [
    "IkeaLedSelectBase",
    "IkeaLedPluginSelect",
    "BrightnessSelect",
    "ColorSelect", 
    "ColorModeSelect",
    "EffectSelect",
    "SpeedSelect",
]
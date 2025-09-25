"""Select platform for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
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
    """Set up the IKEA OBEGRÄNSAD LED select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([IkeaLedPluginSelect(coordinator, entry)])


class IkeaLedPluginSelect(CoordinatorEntity[IkeaLedCoordinator], SelectEntity):
    """Representation of an IKEA OBEGRÄNSAD LED plugin selector."""

    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_plugin_select"
        self._attr_name = "IKEA OBEGRÄNSAD Plugin"
        self._attr_icon = "mdi:format-list-bulleted"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="IKEA OBEGRÄNSAD LED",
            manufacturer="IKEA (Modified)",
            model="OBEGRÄNSAD",
            configuration_url=f"http://{self.coordinator.host}",
        )

    @property
    def options(self) -> list[str]:
        """Return a list of selectable options."""
        if not self.coordinator.data or "plugins" not in self.coordinator.data:
            return []
        
        return [
            f"{plugin.get('name', 'Unknown')}"
            for plugin in self.coordinator.data["plugins"]
        ]

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if not self.coordinator.data:
            return None
            
        current_plugin_id = self.coordinator.data.get("plugin")
        if current_plugin_id is None:
            return None
            
        # Find the matching plugin name
        plugins = self.coordinator.data.get("plugins", [])
        for plugin in plugins:
            if plugin.get("id") == current_plugin_id:
                return f"{plugin.get('id')}: {plugin.get('name', 'Unknown')}"
                
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Extract plugin ID from the option string (format: "ID: Name")
        try:
            plugin_id = int(option.split(":")[0].strip())
            controller = self.coordinator.led_controller
            
            await self.hass.async_add_executor_job(
                controller.set_plugin, plugin_id
            )
            
            # WebSocket will automatically update the state
            
        except (ValueError, IndexError) as ex:
            _LOGGER.error("Failed to parse plugin ID from option: %s", option)
        except Exception as ex:
            _LOGGER.error("Failed to set plugin: %s", ex)
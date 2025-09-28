"""Select entities for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging
from functools import cached_property

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
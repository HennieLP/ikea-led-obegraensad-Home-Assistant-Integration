"""Select platform for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import IkeaLedCoordinator
from .entity import IkeaLedEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IKEA OBEGRÄNSAD LED select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IkeaLedPluginSelect(coordinator, entry)])


def _option(plugin: dict) -> str:
    """Format a plugin as a select option ("ID: Name")."""
    return f"{plugin.get('id')}: {plugin.get('name', 'Unknown')}"


class IkeaLedPluginSelect(IkeaLedEntity, SelectEntity):
    """Representation of an IKEA OBEGRÄNSAD LED plugin selector."""

    _attr_name = "IKEA OBEGRÄNSAD Plugin"
    _attr_icon = "mdi:format-list-bulleted"

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, entry, "plugin_select")

    @property
    def options(self) -> list[str]:
        """Return a list of selectable options."""
        return [_option(plugin) for plugin in (self.coordinator.data or {}).get("plugins", [])]

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        data = self.coordinator.data or {}
        current_plugin_id = data.get("plugin")
        for plugin in data.get("plugins", []):
            if plugin.get("id") == current_plugin_id:
                return _option(plugin)
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            plugin_id = int(option.split(":")[0].strip())
        except ValueError as ex:
            raise HomeAssistantError(f"Unrecognised plugin option: {option}") from ex
        await self.coordinator.async_set_plugin(plugin_id)

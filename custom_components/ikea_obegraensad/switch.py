"""Platform for IKEA OBEGRÄNSAD LED switch integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IKEA OBEGRÄNSAD LED switch platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    factory = data["factory"]
    coordinator = data["coordinator"]
    
    entities = factory.create_entities_for_platform(
        Platform.SWITCH, coordinator, config_entry
    )
    
    async_add_entities(entities, True)

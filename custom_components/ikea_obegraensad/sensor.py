"""Sensor platform for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

# This platform is kept empty as basic functionality doesn't require sensors
# Sensors were removed to keep only the most basic functions:
# - Light entity with dimming (0/255 brightness)
# - Rotate button (90° per click)
# - Plugin selector
# - Schedule toggle switch

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IKEA OBEGRÄNSAD LED sensor platform."""
    # No sensors in basic functionality
    pass

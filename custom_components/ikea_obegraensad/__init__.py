"""The IKEA OBEGRÄNSAD LED Control integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import IkeaLedCoordinator
from .entities.factory import EntityFactory

_LOGGER = logging.getLogger(__name__)

# Initialize the entity factory
_entity_factory = EntityFactory()

# Get platforms from registered entities
PLATFORMS: list[Platform] = _entity_factory.get_platforms()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up IKEA OBEGRÄNSAD LED Control from a config entry."""
    host = entry.data[CONF_HOST]
    
    coordinator = IkeaLedCoordinator(hass, host)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        _LOGGER.exception("Error setting up IKEA OBEGRÄNSAD LED device")
        raise ConfigEntryNotReady from ex

    # Store both coordinator and factory for platforms to use
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "factory": _entity_factory,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN][entry.entry_id]
        coordinator = data["coordinator"]
        await coordinator.async_shutdown()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


def get_entity_factory() -> EntityFactory:
    """Get the global entity factory."""
    return _entity_factory
"""The IKEA OBEGRÄNSAD LED Control integration."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import IkeaLedCoordinator

if TYPE_CHECKING:
    from .entities.factory import EntityFactory

_LOGGER = logging.getLogger(__name__)

# Initialize factory and platforms lazily to avoid import issues during config flow
_entity_factory: EntityFactory | None = None

def _get_entity_factory() -> EntityFactory:
    """Get or create the entity factory."""
    global _entity_factory
    if _entity_factory is None:
        from .entities.factory import EntityFactory
        _entity_factory = EntityFactory()
    return _entity_factory

# Initialize platforms later during setup


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up IKEA OBEGRÄNSAD LED Control from a config entry."""
    host = entry.data[CONF_HOST]
    
    coordinator = IkeaLedCoordinator(hass, host)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        _LOGGER.exception("Error setting up IKEA OBEGRÄNSAD LED device")
        raise ConfigEntryNotReady from ex

    # Get the factory and platforms
    factory = _get_entity_factory()
    platforms = factory.get_platforms()

    # Store both coordinator and factory for platforms to use
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "factory": factory,
    }

    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    factory = _get_entity_factory()
    platforms = factory.get_platforms()
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, platforms):
        data = hass.data[DOMAIN][entry.entry_id]
        coordinator = data["coordinator"]
        await coordinator.async_shutdown()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


def get_entity_factory() -> EntityFactory:
    """Get the global entity factory."""
    factory = _get_entity_factory()
    return factory
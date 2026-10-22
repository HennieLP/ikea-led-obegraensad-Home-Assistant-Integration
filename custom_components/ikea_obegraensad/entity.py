"""Base entity for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import IkeaLedCoordinator


class IkeaLedEntity(CoordinatorEntity[IkeaLedCoordinator]):
    """Common device info and unique id for all entities of one device."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, key: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="IKEA OBEGRÄNSAD LED",
            manufacturer="IKEA (Modified)",
            model="OBEGRÄNSAD",
            configuration_url=f"http://{coordinator.host}",
        )

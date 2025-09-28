"""Base entity class for IKEA OBEGRÄNSAD LED Control entities."""
from __future__ import annotations

import logging
from abc import ABC
from functools import cached_property
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..coordinator import IkeaLedCoordinator

_LOGGER = logging.getLogger(__name__)


class IkeaLedBaseEntity(CoordinatorEntity[IkeaLedCoordinator], ABC):
    """Base class for all IKEA OBEGRÄNSAD LED entities."""

    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
        entity_type: str,
        name: str,
        icon: str | None = None,
        suffix: str = "",
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._entity_type = entity_type
        self._suffix = suffix
        
        # Build unique_id and name
        unique_id_parts = [entry.entry_id, entity_type]
        name_parts = ["IKEA OBEGRÄNSAD", name]
        
        if suffix:
            unique_id_parts.append(suffix)
            name_parts.append(suffix)
            
        self._attr_unique_id = "_".join(unique_id_parts)
        self._attr_name = " ".join(name_parts)
        
        if icon:
            self._attr_icon = icon

    # Override available to resolve inheritance conflict
    @cached_property
    def available(self) -> bool:  # type: ignore[misc]
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @cached_property
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
    def data(self) -> dict[str, Any] | None:
        """Get coordinator data safely."""
        return self.coordinator.data

    def get_data_value(self, key: str, default: Any = None) -> Any:
        """Get a value from coordinator data safely."""
        if not self.data:
            return default
        return self.data.get(key, default)

    async def execute_command(self, command_func: Any, *args: Any, **kwargs: Any) -> None:
        """Execute a coordinator command with error handling."""
        try:
            await self.hass.async_add_executor_job(command_func, *args, **kwargs)
            await self.coordinator.async_refresh_after_command()
        except Exception as ex:
            command_name = getattr(command_func, '__name__', str(command_func))
            _LOGGER.error("Failed to execute %s command: %s", command_name, ex)
            raise
"""Sensor platform for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging
from functools import cached_property
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.ikea_obegraensad.const import DOMAIN
from custom_components.ikea_obegraensad.coordinator import IkeaLedCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IKEA OBEGRÄNSAD LED sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors: list[SensorEntity] = [
        IkeaLedRotationSensor(coordinator, entry),
        IkeaLedActivePluginSensor(coordinator, entry),
    ]
    
    async_add_entities(sensors)


class IkeaLedBaseSensor(CoordinatorEntity[IkeaLedCoordinator], SensorEntity):
    """Base class for IKEA OBEGRÄNSAD LED sensors."""

    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
        name: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_name = f"IKEA OBEGRÄNSAD {name}"
        if icon:
            self._attr_icon = icon

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


class IkeaLedRotationSensor(IkeaLedBaseSensor):
    """Sensor for current rotation value."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the rotation sensor."""
        super().__init__(
            coordinator, 
            entry, 
            "rotation", 
            "Rotation",
            "mdi:rotate-3d-variant"
        )
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @cached_property
    def native_value(self) -> int | None:
        """Return the current rotation value."""
        if not self.coordinator.data:
            return None
        rotation = self.coordinator.data.get("rotation")
        return (90 * rotation) % 360 if rotation is not None else None

    @cached_property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "°"


class IkeaLedActivePluginSensor(IkeaLedBaseSensor):
    """Sensor for current active plugin."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the active plugin sensor."""
        super().__init__(
            coordinator,
            entry,
            "active_plugin",
            "Active Plugin",
            "mdi:puzzle"
        )

    @cached_property
    def native_value(self) -> str | None:
        """Return the current active plugin name."""
        if not self.coordinator.data:
            return None
            
        plugin_id = self.coordinator.data.get("plugin")
        if plugin_id is None:
            return None
            
        # Find the plugin name from available plugins
        plugins = self.coordinator.data.get("plugins", [])
        for plugin in plugins:
            if plugin.get("id") == plugin_id:
                return plugin.get("name", f"Plugin {plugin_id}")
                
        return f"Plugin {plugin_id}"

    @cached_property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return None
            
        return {
            "plugin_id": self.coordinator.data.get("plugin"),
            "available_plugins": [
                {"id": plugin.get("id"), "name": plugin.get("name", "Unknown")}
                for plugin in self.coordinator.data.get("plugins", [])
            ],
        }
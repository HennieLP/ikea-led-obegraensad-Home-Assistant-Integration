"""Sensor entities for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging
from functools import cached_property
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry

from ..coordinator import IkeaLedCoordinator
from ..entities.base import IkeaLedBaseEntity

_LOGGER = logging.getLogger(__name__)


class IkeaLedSensorBase(IkeaLedBaseEntity, SensorEntity):
    """Base class for IKEA OBEGRÄNSAD LED sensors."""
    
    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
        name: str,
        icon: str | None = None,
        unit: str | None = None,
        state_class: SensorStateClass | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "sensor", name, icon, sensor_key)
        if unit:
            self._attr_native_unit_of_measurement = unit
        if state_class:
            self._attr_state_class = state_class


class IkeaLedRotationSensor(IkeaLedSensorBase):
    """Sensor for current rotation value."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the rotation sensor."""
        super().__init__(
            coordinator,
            entry,
            "rotation", 
            "Rotation",
            "mdi:rotate-3d-variant",
            "°",
            SensorStateClass.MEASUREMENT
        )

    @cached_property
    def native_value(self) -> int | None:
        """Return the current rotation value."""
        rotation = self.get_data_value("rotation")
        return (90 * rotation) % 360 if rotation is not None else None


class IkeaLedActivePluginSensor(IkeaLedSensorBase):
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
        plugin_id = self.get_data_value("plugin")
        if plugin_id is None:
            return None
            
        # Find the plugin name from available plugins
        plugins = self.get_data_value("plugins", [])
        for plugin in plugins:
            if plugin.get("id") == plugin_id:
                return plugin.get("name", f"Plugin {plugin_id}")
                
        return f"Plugin {plugin_id}"

    @cached_property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if not self.data:
            return None
            
        return {
            "plugin_id": self.get_data_value("plugin"),
            "available_plugins": [
                {"id": plugin.get("id"), "name": plugin.get("name", "Unknown")}
                for plugin in self.get_data_value("plugins", [])
            ],
        }


class IkeaLedBrightnessSensor(IkeaLedSensorBase):
    """Sensor for brightness level as percentage."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the brightness sensor."""
        super().__init__(
            coordinator,
            entry,
            "brightness",
            "Brightness Level",
            "mdi:brightness-6",
            "%",
            SensorStateClass.MEASUREMENT
        )

    @cached_property
    def native_value(self) -> int | None:
        """Return the current brightness as percentage."""
        brightness = self.get_data_value("brightness", 0)
        return round((brightness / 255) * 100) if brightness is not None else None


class IkeaLedScheduleStatusSensor(IkeaLedSensorBase):
    """Sensor for schedule status."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry) -> None:
        """Initialize the schedule status sensor."""
        super().__init__(
            coordinator,
            entry,
            "schedule_status",
            "Schedule Status",
            "mdi:calendar-clock"
        )

    @cached_property
    def native_value(self) -> str:
        """Return the current schedule status."""
        is_active = self.get_data_value("scheduleActive", False)
        return "Active" if is_active else "Inactive"

    @cached_property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if not self.data:
            return None
            
        return {
            "schedule": self.get_data_value("schedule", []),
            "schedule_active": self.get_data_value("scheduleActive", False),
        }


# Aliases for registry compatibility
BrightnessSensor = IkeaLedBrightnessSensor


class ColorSensor(IkeaLedSensorBase):
    """Sensor for current color."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the color sensor."""
        super().__init__(coordinator, entry, "color_sensor", "Current Color", "mdi:palette")

    @cached_property  # type: ignore[misc]
    def native_value(self) -> str | None:
        """Return the current color."""
        return "RGB(255,255,255)"  # Placeholder


class ColorModeSensor(IkeaLedSensorBase):
    """Sensor for color mode."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the color mode sensor."""
        super().__init__(coordinator, entry, "color_mode_sensor", "Color Mode", "mdi:palette-advanced")

    @cached_property  # type: ignore[misc]
    def native_value(self) -> str | None:
        """Return the current color mode."""
        return "Single"  # Placeholder


class EffectSensor(IkeaLedSensorBase):
    """Sensor for current effect."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the effect sensor."""
        super().__init__(coordinator, entry, "effect_sensor", "Current Effect", "mdi:auto-fix")

    @cached_property  # type: ignore[misc]
    def native_value(self) -> str | None:
        """Return the current effect."""
        return "None"  # Placeholder


class SpeedSensor(IkeaLedSensorBase):
    """Sensor for effect speed."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the speed sensor."""
        super().__init__(coordinator, entry, "speed_sensor", "Effect Speed", "mdi:speedometer")

    @cached_property  # type: ignore[misc]
    def native_value(self) -> str | None:
        """Return the current speed."""
        return "Medium"  # Placeholder


class PowerStateSensor(IkeaLedSensorBase):
    """Sensor for power state."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the power state sensor."""
        super().__init__(coordinator, entry, "power_state_sensor", "Power State", "mdi:power")

    @cached_property  # type: ignore[misc]
    def native_value(self) -> str | None:
        """Return the power state."""
        brightness = self.get_data_value("brightness", 0)
        return "On" if brightness > 0 else "Off"


class ConnectionStateSensor(IkeaLedSensorBase):
    """Sensor for connection state."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the connection sensor."""
        super().__init__(coordinator, entry, "connection_sensor", "Connection State", "mdi:connection")

    @cached_property  # type: ignore[misc]
    def native_value(self) -> str | None:
        """Return the connection state."""
        return "Connected" if self.coordinator.last_update_success else "Disconnected"


class LastCommandSensor(IkeaLedSensorBase):
    """Sensor for last command."""

    def __init__(self, coordinator: IkeaLedCoordinator, entry: ConfigEntry, config: Any) -> None:
        """Initialize the last command sensor."""
        super().__init__(coordinator, entry, "last_command_sensor", "Last Command", "mdi:console-line")

    @cached_property  # type: ignore[misc]
    def native_value(self) -> str | None:
        """Return the last command."""
        return "None"  # Placeholder


__all__ = [
    "IkeaLedSensorBase",
    "IkeaLedRotationSensor",
    "IkeaLedActivePluginSensor", 
    "IkeaLedBrightnessSensor",
    "IkeaLedScheduleStatusSensor",
    "BrightnessSensor",
    "ColorSensor",
    "ColorModeSensor", 
    "EffectSensor",
    "SpeedSensor",
    "PowerStateSensor",
    "ConnectionStateSensor",
    "LastCommandSensor",
]
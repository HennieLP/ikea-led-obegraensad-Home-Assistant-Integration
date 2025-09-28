"""Entity registry for managing entity configurations."""
from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from ..coordinator import IkeaLedCoordinator

_LOGGER = logging.getLogger(__name__)


class EntityType(Enum):
    """Entity types for the registry."""
    LIGHT = "light"
    BUTTON = "button"
    SELECT = "select"
    SENSOR = "sensor"
    SWITCH = "switch"


@dataclass
class EntityConfig:
    """Configuration for an entity."""
    key: str
    name: str
    icon: str | None
    entity_type: EntityType
    entity_class: type[Any]
    device_class: str | None = None
    unit_of_measurement: str | None = None
    state_class: str | None = None
    options: list[str] | None = None
    translation_key: str | None = None
    extra_attributes: list[str] = field(default_factory=lambda: [])
    prerequisites: list[str] = field(default_factory=lambda: [])
    conditions: dict[str, Any] = field(default_factory=lambda: {})


class EntityRegistry:
    """Registry for entity configurations."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self.entities: dict[str, EntityConfig] = {}
        self._setup_default_entities()

    def _setup_default_entities(self) -> None:
        """Set up default entity configurations."""
        from .buttons import (
            RestartButton,
            ResetButton,
            PowerToggleButton,
            BrightnessDownButton,
            BrightnessUpButton,
        )
        from .lights import MainLight
        from .selects import (
            BrightnessSelect,
            ColorSelect,
            ColorModeSelect,
            EffectSelect,
            SpeedSelect,
        )
        from .sensors import (
            BrightnessSensor,
            ColorSensor,
            ColorModeSensor,
            EffectSensor,
            SpeedSensor,
            PowerStateSensor,
            ConnectionStateSensor,
            LastCommandSensor,
        )
        from .switches import (
            PowerSwitch,
            EffectSwitch,
            AutoBrightnessSwitch,
        )

        # Light entities
        self.register_entity(EntityConfig(
            key="main_light",
            name="Main Light",
            icon="mdi:lightbulb",
            entity_type=EntityType.LIGHT,
            entity_class=MainLight,
        ))

        # Button entities
        self.register_entity(EntityConfig(
            key="restart_button",
            name="Restart Device",
            icon="mdi:restart",
            entity_type=EntityType.BUTTON,
            entity_class=RestartButton,
        ))

        self.register_entity(EntityConfig(
            key="reset_button",
            name="Reset to Default",
            icon="mdi:backup-restore",
            entity_type=EntityType.BUTTON,
            entity_class=ResetButton,
        ))

        self.register_entity(EntityConfig(
            key="power_toggle_button",
            name="Power Toggle",
            icon="mdi:power",
            entity_type=EntityType.BUTTON,
            entity_class=PowerToggleButton,
        ))

        self.register_entity(EntityConfig(
            key="brightness_down_button",
            name="Brightness Down",
            icon="mdi:brightness-4",
            entity_type=EntityType.BUTTON,
            entity_class=BrightnessDownButton,
        ))

        self.register_entity(EntityConfig(
            key="brightness_up_button",
            name="Brightness Up",
            icon="mdi:brightness-7",
            entity_type=EntityType.BUTTON,
            entity_class=BrightnessUpButton,
        ))

        # Select entities
        self.register_entity(EntityConfig(
            key="brightness_select",
            name="Brightness Level",
            icon="mdi:brightness-6",
            entity_type=EntityType.SELECT,
            entity_class=BrightnessSelect,
            options=["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"],
        ))

        self.register_entity(EntityConfig(
            key="color_select",
            name="Color Preset",
            icon="mdi:palette",
            entity_type=EntityType.SELECT,
            entity_class=ColorSelect,
            options=["Red", "Green", "Blue", "White", "Yellow", "Cyan", "Magenta", "Orange"],
        ))

        self.register_entity(EntityConfig(
            key="color_mode_select",
            name="Color Mode",
            icon="mdi:palette-advanced",
            entity_type=EntityType.SELECT,
            entity_class=ColorModeSelect,
            options=["Single", "Rainbow", "Fade", "Strobe"],
        ))

        self.register_entity(EntityConfig(
            key="effect_select",
            name="Effect",
            icon="mdi:auto-fix",
            entity_type=EntityType.SELECT,
            entity_class=EffectSelect,
            options=["None", "Fade", "Strobe", "Rainbow", "Color Cycle"],
        ))

        self.register_entity(EntityConfig(
            key="speed_select",
            name="Effect Speed",
            icon="mdi:speedometer",
            entity_type=EntityType.SELECT,
            entity_class=SpeedSelect,
            options=["Slow", "Medium", "Fast"],
        ))

        # Sensor entities
        self.register_entity(EntityConfig(
            key="brightness_sensor",
            name="Brightness Level",
            icon="mdi:brightness-6",
            entity_type=EntityType.SENSOR,
            entity_class=BrightnessSensor,
            unit_of_measurement="%",
            state_class="measurement",
        ))

        self.register_entity(EntityConfig(
            key="color_sensor",
            name="Current Color",
            icon="mdi:palette",
            entity_type=EntityType.SENSOR,
            entity_class=ColorSensor,
        ))

        self.register_entity(EntityConfig(
            key="color_mode_sensor",
            name="Color Mode",
            icon="mdi:palette-advanced",
            entity_type=EntityType.SENSOR,
            entity_class=ColorModeSensor,
        ))

        self.register_entity(EntityConfig(
            key="effect_sensor",
            name="Current Effect",
            icon="mdi:auto-fix",
            entity_type=EntityType.SENSOR,
            entity_class=EffectSensor,
        ))

        self.register_entity(EntityConfig(
            key="speed_sensor",
            name="Effect Speed",
            icon="mdi:speedometer",
            entity_type=EntityType.SENSOR,
            entity_class=SpeedSensor,
        ))

        self.register_entity(EntityConfig(
            key="power_state_sensor",
            name="Power State",
            icon="mdi:power",
            entity_type=EntityType.SENSOR,
            entity_class=PowerStateSensor,
            device_class="power",
        ))

        self.register_entity(EntityConfig(
            key="connection_state_sensor",
            name="Connection State",
            icon="mdi:connection",
            entity_type=EntityType.SENSOR,
            entity_class=ConnectionStateSensor,
            device_class="connectivity",
        ))

        self.register_entity(EntityConfig(
            key="last_command_sensor",
            name="Last Command",
            icon="mdi:console-line",
            entity_type=EntityType.SENSOR,
            entity_class=LastCommandSensor,
        ))

        # Switch entities
        self.register_entity(EntityConfig(
            key="power_switch",
            name="Power",
            icon="mdi:power",
            entity_type=EntityType.SWITCH,
            entity_class=PowerSwitch,
            device_class="switch",
        ))

        self.register_entity(EntityConfig(
            key="effect_switch",
            name="Effect Mode",
            icon="mdi:auto-fix",
            entity_type=EntityType.SWITCH,
            entity_class=EffectSwitch,
        ))

        self.register_entity(EntityConfig(
            key="auto_brightness_switch",
            name="Auto Brightness",
            icon="mdi:brightness-auto",
            entity_type=EntityType.SWITCH,
            entity_class=AutoBrightnessSwitch,
        ))

    def register_entity(self, config: EntityConfig) -> None:
        """Register an entity configuration."""
        self.entities[config.key] = config

    def get_entities_for_platform(self, platform: Platform) -> list[EntityConfig]:
        """Get all entities for a specific platform."""
        return [
            config for config in self.entities.values()
            if config.entity_type.value == platform.value
        ]

    def create_entity_instance(
        self, key: str, coordinator: IkeaLedCoordinator, entry: ConfigEntry
    ) -> Any:
        """Create an entity instance from configuration."""
        config = self.entities.get(key)
        if not config:
            raise ValueError(f"Entity configuration not found for key: {key}")
        
        # Inspect the constructor to determine if it expects a config parameter
        init_signature = inspect.signature(config.entity_class.__init__)
        params = list(init_signature.parameters.keys())
        
        # Remove 'self' parameter from consideration
        params = params[1:] if params and params[0] == 'self' else params
        
        # Call constructor with appropriate parameters
        if len(params) >= 3:
            # Constructor expects coordinator, entry, and config
            return config.entity_class(coordinator, entry, config)
        else:
            # Constructor expects only coordinator and entry
            return config.entity_class(coordinator, entry)

    def get_platforms(self) -> list[Platform]:
        """Get all platforms that have registered entities."""
        platforms: set[str] = set()
        for config in self.entities.values():
            platforms.add(config.entity_type.value)
        return [Platform(platform) for platform in platforms]

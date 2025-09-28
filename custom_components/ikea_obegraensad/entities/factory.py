"""Entity factory for creating entities dynamically."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from ..coordinator import IkeaLedCoordinator
from .registry import EntityConfig, EntityRegistry, EntityType

_LOGGER = logging.getLogger(__name__)


class EntityFactory:
    """Factory for creating entities based on available data and configuration."""
    
    def __init__(self) -> None:
        """Initialize the factory."""
        self.registry = EntityRegistry()

    def create_entities_for_platform(
        self,
        platform: Platform,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
    ) -> list[Any]:
        """Create all entities for a specific platform."""
        entities = []
        
        # Get entities for this platform
        entity_configs = self.registry.get_entities_for_platform(platform)
        
        for config in entity_configs:
            try:
                # Check if entity should be created based on available data
                if coordinator.data and not self._is_entity_available(config, coordinator.data):
                    _LOGGER.debug("Skipping unavailable entity: %s (missing prerequisites)", config.key)
                    continue
                
                # Create the entity instance
                entity = self.registry.create_entity_instance(config.key, coordinator, entry)
                entities.append(entity)
                _LOGGER.debug("Created entity: %s (%s)", config.key, config.name)
            except Exception as ex:
                _LOGGER.error("Failed to create entity %s: %s", config.key, ex)
        
        return entities

    def _is_entity_available(self, config: EntityConfig, coordinator_data: dict[str, Any]) -> bool:
        """Check if an entity should be available based on its prerequisites and conditions."""
        # Check prerequisites (required data keys)
        for prerequisite in config.prerequisites:
            if prerequisite not in coordinator_data:
                return False
        
        # Check conditions (specific data values)
        for key, expected_value in config.conditions.items():
            if coordinator_data.get(key) != expected_value:
                return False
                
        return True

    def get_platforms(self) -> list[Platform]:
        """Get all platforms that have registered entities."""
        return self.registry.get_platforms()

    def get_entity_config(self, key: str) -> EntityConfig | None:
        """Get entity configuration by key."""
        return self.registry.entities.get(key)

    def is_entity_available(self, key: str, coordinator_data: dict[str, Any]) -> bool:
        """Check if a specific entity is available."""
        config = self.get_entity_config(key)
        if not config:
            return False
        return self._is_entity_available(config, coordinator_data)

# IKEA OBEGRÄNSAD LED Control - Home Assistant Integration

## Architecture Overview

This integration has been refactored to use a modular, extensible architecture that makes it easy to add new features, sensors, and switches. The codebase now follows strict Pylance standards and implements a factory pattern for entity creation.

## New Modular Structure

```
custom_components/ikea_obegraensad/
├── __init__.py                 # Main integration setup with entity factory
├── coordinator.py              # Data coordinator for WebSocket communication
├── config_flow.py             # Configuration flow
├── const.py                   # Constants
├── *.py                       # Platform files (simplified, use factory)
└── entities/                  # New modular entity system
    ├── __init__.py            # Entity module exports
    ├── base.py                # Base entity class
    ├── registry.py            # Entity configuration registry
    ├── factory.py             # Entity factory for dynamic creation
    ├── lights.py              # Light entity implementations
    ├── sensors.py             # Sensor entity implementations
    ├── buttons.py             # Button entity implementations
    ├── selects.py             # Select entity implementations
    └── switches.py            # Switch entity implementations
```

## Key Features

### 1. Entity Registry System
- **File**: `entities/registry.py`
- **Purpose**: Centralized configuration for all entities
- **Benefits**: Easy to add new entities by registering them in one place

### 2. Entity Factory Pattern  
- **File**: `entities/factory.py`
- **Purpose**: Dynamic entity creation based on available data
- **Benefits**: Automatically creates only entities that have required data available

### 3. Base Entity Class
- **File**: `entities/base.py`
- **Purpose**: Common functionality for all entities
- **Benefits**: Reduces code duplication and ensures consistency

### 4. Modular Entity Classes
- **Files**: `entities/{lights,sensors,buttons,selects,switches}.py`
- **Purpose**: Specific implementations for each entity type
- **Benefits**: Clean separation of concerns, easy to extend

## Adding New Entities

### Step 1: Create the Entity Class
Add your new entity to the appropriate module (e.g., `entities/sensors.py`):

```python
class NewCustomSensor(IkeaLedBaseEntity, SensorEntity):
    """Custom sensor implementation."""
    
    def __init__(
        self,
        coordinator: IkeaLedCoordinator,
        entry: ConfigEntry,
        config: EntityConfig,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, config)
        # Custom initialization
    
    @cached_property  # type: ignore[misc]
    def native_value(self) -> str | None:
        """Return the sensor value."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("your_data_key")
```

### Step 2: Register the Entity
Add the entity to the registry in `entities/registry.py`:

```python
# In _setup_default_entities method
self.register_entity(EntityConfig(
    key="new_custom_sensor",
    name="New Custom Sensor", 
    icon="mdi:your-icon",
    entity_type=EntityType.SENSOR,
    entity_class=NewCustomSensor,
    unit_of_measurement="your_unit",  # Optional
    device_class="your_device_class", # Optional
    prerequisites=["required_data_key"],  # Optional: required data keys
))
```

### Step 3: Export the Entity (Optional)
Add to `entities/sensors.py` exports if needed:

```python
__all__ = [
    "BrightnessSensor",
    "ColorSensor", 
    # ... existing exports
    "NewCustomSensor",  # Add your new sensor
]
```

That's it! The factory will automatically:
- Detect the new entity configuration
- Create instances only when required data is available
- Add the entity to the appropriate platform

## Adding New Platforms

To add a completely new platform type:

1. Create a new `EntityType` in `entities/registry.py`
2. Create a new module file (e.g., `entities/numbers.py`)
3. Create platform file (e.g., `number.py`) that uses the factory
4. Register entities in the registry

## Prerequisites and Conditions

The registry supports conditional entity creation:

```python
EntityConfig(
    key="conditional_entity",
    name="Conditional Entity",
    # ... other config
    prerequisites=["required_data_key"],  # Must exist in coordinator.data
    conditions={"some_key": "some_value"}  # Additional conditions
)
```

## Benefits of This Architecture

1. **Extensible**: Easy to add new entities without modifying existing code
2. **Maintainable**: Clear separation of concerns and single responsibility
3. **Type Safe**: Full Pylance compliance with proper type annotations
4. **Dynamic**: Entities are created only when their data is available
5. **Consistent**: All entities share common base functionality
6. **Testable**: Modular design makes unit testing easier

## Migration from Old Architecture

The old monolithic platform files have been replaced with simple factory-based files. All entity logic has been moved to the modular `entities/` directory. This provides:

- Better code organization
- Easier testing and debugging  
- Simpler addition of new features
- Consistent entity behavior
- Better error handling and validation

## Development Workflow

1. **Adding Features**: Add to appropriate entity module and register
2. **Debugging**: Check entity-specific modules for isolated issues
3. **Testing**: Each entity type can be tested independently
4. **Documentation**: Entity configurations are self-documenting in registry

This architecture makes the integration much more maintainable and extensible for future development.
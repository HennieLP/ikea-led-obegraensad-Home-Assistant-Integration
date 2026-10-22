# Simplification Summary

## What was changed

This branch (dev) has been simplified to keep only the most basic functionality as requested:

### ✅ Kept Core Features:
1. **HA Light Entity** - Brightness control with dimming (0/255) and on/off functionality
2. **Rotate Button** - Single button that rotates the display 90° per click 
3. **Plugin Selector** - Dropdown to select the currently active plugin
4. **Schedule Toggle Switch** - Turn the scheduler on/off

### 🗑️ Removed Complex Architecture:
- Removed the entire modular `entities/` directory with factory pattern
- Removed complex EntityRegistry and EntityFactory classes  
- Removed ARCHITECTURE.md and REFACTORING_SUMMARY.md documentation
- Simplified all platform files to use direct entity implementations
- Removed sensors platform (not needed for basic functionality)
- Removed extra buttons (rotate left/right → single rotate button)

### 📁 File Structure Now:
```
custom_components/ikea_obegraensad/
├── __init__.py          # Simple platform setup (light, button, select, switch)
├── coordinator.py       # WebSocket (aiohttp, on HA's event loop) + HTTP fallback
├── light.py            # Single light entity with brightness control
├── button.py           # Single rotate button (90° per click)
├── select.py           # Plugin selector dropdown
├── switch.py           # Schedule toggle switch  
├── entity.py           # Shared base entity (device info, unique id)
├── config_flow.py      # Configuration (unchanged)
├── const.py            # Constants (unchanged)
├── manifest.json       # Integration manifest
└── strings.json        # UI strings
```

### 🔧 Implementation Details:
- **Light Entity**: Uses CoordinatorEntity, supports brightness 0-255, shows extra attributes (plugin, rotation, schedule status, available plugins)
- **Rotate Button**: Single button that calls `coordinator.async_rotate("right")` to rotate 90°
- **Plugin Select**: Shows all available plugins as "ID: Name" format, calls `coordinator.async_set_plugin(plugin_id)`
- **Schedule Switch**: Shows current schedule state, calls `coordinator.async_set_schedule_active(bool)` (HTTP `/api/schedule/start|stop`)

### ⚡ Coordinator Features Used:
- `async_set_brightness(brightness)` - Set brightness 0-255
- `async_rotate("right")` - Rotate display 90° clockwise  
- `async_set_plugin(plugin_id)` - Change active plugin
- `async_set_schedule_active(active)` - Start/stop the stored schedule
- WebSocket real-time updates for all state changes

This simplified version maintains the original clean architecture from the main branch while providing exactly the 4 basic features requested, keeping the existing modular file structure but removing the complex factory pattern that was over-engineered for the requirements.
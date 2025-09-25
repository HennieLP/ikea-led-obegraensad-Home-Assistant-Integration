# IKEA OBEGRÄNSAD LED Control

Python Package and Home Assistant Integration to control the modified IKEA OBEGRÄNSAD LED wall lamp.

This project provides:
1. **Python Library** - Direct control of the LED device from Python applications
2. **Home Assistant HACS Integration** - Full Home Assistant integration with lights, sensors, buttons, and selects

## Hardware Requirements

You need a modified IKEA OBEGRÄNSAD LED wall lamp with ESP32 running the custom firmware from [ph1p/ikea-led-obegraensad](https://github.com/ph1p/ikea-led-obegraensad).

## Python Library Usage

### Installation

```bash
pip install ikea-led-obegraensad-python-control
```

### Basic Usage

```python
import ikea_led_obegraensad_python_control

# Connect to your device
light = ikea_led_obegraensad_python_control.setup("192.168.1.100")

# Control the light
light.turn_on()
light.set_brightness(128)
light.set_plugin(5)
light.set_rotation("left")

# Get device information
info = light.get_info()
print(f"Current brightness: {info['brightness']}")
print(f"Active plugin: {info['plugin']}")
```

### Available Methods

- `turn_on()` - Turn on the LED display
- `turn_off()` - Turn off the LED display  
- `set_brightness(value)` - Set brightness (0-255)
- `set_plugin(plugin_id)` - Set active plugin
- `set_rotation(direction)` - Rotate display ("left" or "right")
- `get_info()` - Get current device state
- `get_brightness()` - Get current brightness
- `get_rotation()` - Get current rotation
- `get_active_plugin()` - Get active plugin ID
- `get_available_plugins()` - Get list of available plugins
- `get_schedule_state()` - Get schedule status
- `get_schedule()` - Get current schedule

## Home Assistant Integration

This integration provides complete Home Assistant control of your IKEA OBEGRÄNSAD LED device through HACS.

### Installation

1. Install via HACS:
   - Go to HACS → Integrations
   - Click the three dots → Custom repositories
   - Add this repository URL: `https://github.com/HennieLP/ikea-led-obegraensad-python-control`
   - Category: Integration
   - Install "IKEA OBEGRÄNSAD LED Control"

2. Restart Home Assistant

3. Add the integration:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "IKEA OBEGRÄNSAD LED Control"
   - Enter your device's IP address

### Entities Created

The integration creates the following entities:

#### Light
- **IKEA OBEGRÄNSAD LED** - Main light with brightness control

#### Select
- **IKEA OBEGRÄNSAD Plugin** - Choose between available plugins/display modes

#### Sensors
- **IKEA OBEGRÄNSAD Rotation** - Current display rotation
- **IKEA OBEGRÄNSAD Active Plugin** - Currently active plugin name
- **IKEA OBEGRÄNSAD Schedule Status** - Schedule active/inactive
- **IKEA OBEGRÄNSAD Brightness** - Current brightness percentage

#### Buttons
- **IKEA OBEGRÄNSAD Rotate Left** - Rotate display counterclockwise
- **IKEA OBEGRÄNSAD Rotate Right** - Rotate display clockwise

### Example Automations

```yaml
# Dim display at sunset
alias: "Dim IKEA LED at sunset"
trigger:
  - platform: sun
    event: sunset
action:
  - service: light.turn_on
    target:
      entity_id: light.ikea_obegraensad_led
    data:
      brightness: 50

# Change plugin based on time of day
alias: "Change IKEA LED plugin by time"
trigger:
  - platform: time
    at: "08:00:00"
  - platform: time
    at: "18:00:00"
action:
  - choose:
      - conditions:
          - condition: time
            after: "08:00:00"
            before: "18:00:00"
        sequence:
          - service: select.select_option
            target:
              entity_id: select.ikea_obegraensad_plugin  
            data:
              option: "1: Clock"
      - conditions:
          - condition: time
            after: "18:00:00"
        sequence:
          - service: select.select_option
            target:
              entity_id: select.ikea_obegraensad_plugin
            data:
              option: "5: Mood Lighting"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Credits

- Hardware modification and ESP32 firmware: [ph1p/ikea-led-obegraensad](https://github.com/ph1p/ikea-led-obegraensad)
- Python library and Home Assistant integration: This project

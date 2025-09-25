# IKEA OBEGRÄNSAD LED Control Integration

This Home Assistant custom integration provides control for the modified IKEA OBEGRÄNSAD LED wall lamp via your existing Python control library.

## What You Get

After installing this integration, you'll have the following entities for your IKEA OBEGRÄNSAD LED device:

### Light Entity

- **IKEA OBEGRÄNSAD LED** - Main light control with brightness adjustment
  - Turn on/off the display
  - Control brightness (0-255)
  - View current plugin, rotation, and schedule status as attributes

### Select Entity

- **IKEA OBEGRÄNSAD Plugin** - Choose between available plugins/display modes
  - Switch between different visual plugins
  - Shows all available plugins as options

### Sensor Entities

- **IKEA OBEGRÄNSAD Rotation** - Current display rotation angle
- **IKEA OBEGRÄNSAD Active Plugin** - Name of currently active plugin  
- **IKEA OBEGRÄNSAD Schedule Status** - Whether plugin scheduling is active
- **IKEA OBEGRÄNSAD Brightness** - Current brightness level with percentage

### Button Entities

- **IKEA OBEGRÄNSAD Rotate Left** - Rotate the display counterclockwise
- **IKEA OBEGRÄNSAD Rotate Right** - Rotate the display clockwise

## Requirements

- Modified IKEA OBEGRÄNSAD LED lamp with ESP32 running the custom firmware
- Device accessible on your local network
- The Python control library (included with this integration)

## Setup

1. Install this integration through HACS
2. Restart Home Assistant  
3. Go to **Settings** → **Devices & Services**
4. Click **Add Integration** and search for "IKEA OBEGRÄNSAD LED Control"
5. Enter the IP address of your modified IKEA LED device
6. The integration will automatically discover and set up all entities

## Configuration

The integration only requires the IP address of your device. All other configuration is automatic.

## Support

For issues with this integration, please visit the [GitHub repository](https://github.com/HennieLP/ikea-led-obegraensad-python-control).

For issues with the hardware modification or ESP32 firmware, please visit the [original project](https://github.com/ph1p/ikea-led-obegraensad).
# Installation Guide

## For Python Library

### Install from PyPI (when published)
```bash
pip install ikea-led-obegraensad-python-control
```

### Install from Source
```bash
git clone https://github.com/HennieLP/ikea-led-obegraensad-python-control.git
cd ikea-led-obegraensad-python-control
pip install -e .
```

### Try the Demo
```bash
python demo.py
```

## For Home Assistant Integration

### Via HACS (Recommended)
1. Ensure HACS is installed in your Home Assistant instance
2. Go to HACS → Integrations
3. Click the three dots menu → Custom repositories  
4. Add repository URL: `https://github.com/HennieLP/ikea-led-obegraensad-python-control`
5. Category: Integration
6. Click "Add"
7. Find "IKEA OBEGRÄNSAD LED Control" and install
8. Restart Home Assistant
9. Go to Settings → Devices & Services → Add Integration
10. Search for "IKEA OBEGRÄNSAD LED Control" and configure with your device IP

### Manual Installation
1. Download the `custom_components/ikea_obegraensad` folder
2. Copy it to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Add the integration via Settings → Devices & Services

## Hardware Requirements

- Modified IKEA OBEGRÄNSAD LED wall lamp with ESP32
- ESP32 running firmware from [ph1p/ikea-led-obegraensad](https://github.com/ph1p/ikea-led-obegraensad)
- Device connected to your local network

## Configuration

The only configuration needed is the IP address of your IKEA OBEGRÄNSAD LED device.
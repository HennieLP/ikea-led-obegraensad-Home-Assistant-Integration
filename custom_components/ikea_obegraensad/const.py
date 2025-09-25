"""Constants for the IKEA OBEGRÄNSAD LED Control integration."""

DOMAIN = "ikea_obegraensad"

# Configuration
CONF_HOST = "host"

# Default values
DEFAULT_NAME = "IKEA OBEGRÄNSAD LED"
DEFAULT_PORT = 80
# Fallback update interval (WebSocket provides real-time updates)
DEFAULT_UPDATE_INTERVAL = 300  # 5 minutes as fallback only

# Attributes
ATTR_PLUGIN = "plugin"
ATTR_ROTATION = "rotation"
ATTR_SCHEDULE_ACTIVE = "schedule_active"
ATTR_AVAILABLE_PLUGINS = "available_plugins"
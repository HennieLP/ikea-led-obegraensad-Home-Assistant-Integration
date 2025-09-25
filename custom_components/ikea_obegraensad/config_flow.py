"""Config flow for IKEA OBEGRÄNSAD LED Control integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IKEA OBEGRÄNSAD LED Control."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            host = user_input[CONF_HOST]
            
            # Test connection
            try:
                await self._test_connection(host)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=f"IKEA OBEGRÄNSAD LED ({host})",
                    data={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _test_connection(self, host: str) -> bool:
        """Test if we can connect to the device."""
        try:
            # Import the library dynamically
            import ikea_led_obegraensad_python_control
            
            # Create controller instance
            controller = ikea_led_obegraensad_python_control.setup(host)
            
            # Test connection by getting device info with timeout
            info = await self.hass.async_add_executor_job(controller.get_info)
            
            if not info or not isinstance(info, dict):
                _LOGGER.warning("Device at %s returned invalid info: %s", host, info)
                raise CannotConnect
            
            # Verify we have expected fields in the response
            required_fields = ["brightness"]  # Minimum required field
            if not any(field in info for field in required_fields):
                _LOGGER.warning("Device at %s returned unexpected info format: %s", host, info)
                raise CannotConnect
                
            _LOGGER.info("Successfully connected to IKEA LED device at %s", host)
            return True
            
        except ConnectionError as ex:
            _LOGGER.error("Network connection failed for device at %s: %s", host, ex)
            raise CannotConnect from ex
        except TimeoutError as ex:
            _LOGGER.error("Connection timeout for device at %s: %s", host, ex)
            raise CannotConnect from ex
        except Exception as ex:
            _LOGGER.exception("Error connecting to IKEA LED device at %s", host)
            raise CannotConnect from ex


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
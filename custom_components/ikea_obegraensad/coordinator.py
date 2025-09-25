"""Data update coordinator for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging
import asyncio
from datetime import timedelta
from typing import Any, Callable

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class IkeaLedCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the IKEA OBEGRÄNSAD LED device."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize."""
        self.host = host
        self._led_controller = None
        self._state_callback_registered = False
        
        # Use a longer update interval since we rely on WebSocket updates
        # This is just a fallback in case WebSocket connection fails
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),  # Much longer interval as fallback
        )

    async def _async_setup_controller(self) -> None:
        """Set up the LED controller."""
        if self._led_controller is None:
            try:
                # Import the library using relative import
                from . import ikea_led_obegraensad_python_control
                
                self._led_controller = ikea_led_obegraensad_python_control.setup(self.host)
                
                # Monkey patch the WebSocket message handler to trigger HA updates
                if not self._state_callback_registered:
                    await self._setup_websocket_callback()
                    self._state_callback_registered = True
                    
            except Exception as ex:
                _LOGGER.exception("Failed to set up IKEA LED controller")
                raise UpdateFailed(f"Error setting up controller: {ex}") from ex

    async def _setup_websocket_callback(self) -> None:
        """Set up callback to trigger HA updates when WebSocket receives data."""
        if not self._led_controller:
            return
            
        # Store the original handler
        original_handler = self._led_controller._handle_ws_message
        
        # Create a new handler that calls the original and then triggers HA update
        async def enhanced_handler(message: str):
            await original_handler(message)
            # Schedule HA state update on the event loop
            self.hass.async_create_task(self._trigger_ha_update())
        
        # Replace the handler
        self._led_controller._handle_ws_message = enhanced_handler

    async def _trigger_ha_update(self) -> None:
        """Trigger a Home Assistant state update."""
        try:
            # Get current state from the controller
            current_data = await self.hass.async_add_executor_job(self._led_controller.get_info)
            
            # Update the coordinator's data
            self.data = current_data
            
            # Notify all listeners (entities) of the update
            self.async_update_listeners()
            
            _LOGGER.debug("Triggered HA update from WebSocket data")
            
        except Exception as ex:
            _LOGGER.warning("Failed to trigger HA update from WebSocket: %s", ex)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library - used as fallback."""
        await self._async_setup_controller()
        
        try:
            # Run the synchronous get_info method in executor
            info = await self.hass.async_add_executor_job(self._led_controller.get_info)
            _LOGGER.debug("Fallback poll update completed")
            return info
        except Exception as ex:
            _LOGGER.exception("Error fetching data from IKEA LED device")
            raise UpdateFailed(f"Error communicating with device at {self.host}: {ex}") from ex

    @property
    def led_controller(self):
        """Return the LED controller."""
        return self._led_controller

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        if self._led_controller:
            # Clean up WebSocket connections if needed
            _LOGGER.info("Shutting down IKEA LED coordinator")
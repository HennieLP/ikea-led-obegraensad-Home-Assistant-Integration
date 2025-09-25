"""Data update coordinator for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class IkeaLedCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the IKEA OBEGRÄNSAD LED device."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize."""
        self.host = host
        self._led_controller = None
        self._websocket_task = None
        
        # Use moderate update interval - WebSocket provides real-time updates
        # but we need some polling as fallback
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),  # More frequent as fallback
        )

    async def _async_setup_controller(self) -> None:
        """Set up the LED controller."""
        if self._led_controller is None:
            try:
                # Import the library using relative import
                from . import ikea_led_obegraensad_python_control
                
                self._led_controller = ikea_led_obegraensad_python_control.setup(self.host)
                
                # Give WebSocket some time to establish connection
                await asyncio.sleep(2)
                
                _LOGGER.info("IKEA LED controller setup completed for %s", self.host)
                    
            except Exception as ex:
                _LOGGER.exception("Failed to set up IKEA LED controller")
                raise UpdateFailed(f"Error setting up controller: {ex}") from ex

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        await self._async_setup_controller()
        
        try:
            # Run the synchronous get_info method in executor
            info = await self.hass.async_add_executor_job(self._led_controller.get_info)
            
            # Check if we have a WebSocket connection
            ws_status = "connected" if (
                hasattr(self._led_controller, 'ws_connected') and 
                self._led_controller.ws_connected
            ) else "disconnected"
            
            _LOGGER.debug("Data update completed, WebSocket: %s", ws_status)
            
            if not info:
                raise UpdateFailed("No data received from device")
                
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
        if self._websocket_task:
            self._websocket_task.cancel()
            try:
                await self._websocket_task
            except asyncio.CancelledError:
                pass
                
        if self._led_controller:
            # Clean up WebSocket connections if needed
            _LOGGER.info("Shutting down IKEA LED coordinator")

    async def async_refresh_after_command(self) -> None:
        """Refresh data after sending a command - with delay to allow WebSocket update."""
        # Small delay to allow WebSocket to receive the update first
        await asyncio.sleep(0.5)
        await self.async_request_refresh()
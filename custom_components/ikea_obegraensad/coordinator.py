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
        self._monitoring_callback_registered = False
        
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
                
                # Hook into the monitoring system for WebSocket updates
                if not self._monitoring_callback_registered:
                    self._setup_websocket_monitoring()
                    self._monitoring_callback_registered = True
                
                _LOGGER.info("IKEA LED controller setup completed for %s", self.host)
                    
            except Exception as ex:
                _LOGGER.exception("Failed to set up IKEA LED controller")
                raise UpdateFailed(f"Error setting up controller: {ex}") from ex

    def _setup_websocket_monitoring(self) -> None:
        """Set up monitoring of WebSocket state changes."""
        if not self._led_controller:
            return
            
        # Store the original monitor_changes function
        original_monitor = self._led_controller._start_monitoring
        
        # Create an enhanced monitor that includes HA updates
        def enhanced_monitor():
            def monitor_changes():
                import time
                while True:
                    try:
                        with self._led_controller._ws_lock:
                            current_state = dict(self._led_controller._state)
                        
                        # Check for changes and trigger HA updates
                        for key, value in current_state.items():
                            if key not in self._led_controller._last_state or self._led_controller._last_state[key] != value:
                                if key in self._led_controller._last_state:  # Don't log initial values
                                    print(f"Change detected: {key} changed from {self._led_controller._last_state[key]} to {value}")
                                    # Schedule HA update on the main thread
                                    self.hass.loop.call_soon_threadsafe(
                                        lambda: self.hass.async_create_task(self._on_websocket_change())
                                    )
                                self._led_controller._last_state[key] = value
                        
                        time.sleep(0.5)  # Check every 500ms
                    except Exception as e:
                        # Silently continue if there's an error getting state
                        time.sleep(1)
            
            import threading
            self._led_controller._monitor_thread = threading.Thread(target=monitor_changes, daemon=True)
            self._led_controller._monitor_thread.start()
        
        # Replace the monitoring function
        self._led_controller._start_monitoring = enhanced_monitor
        
        # If monitoring hasn't started yet, start it now with our enhanced version
        if not hasattr(self._led_controller, '_monitor_thread') or not self._led_controller._monitor_thread.is_alive():
            enhanced_monitor()

    async def _on_websocket_change(self) -> None:
        """Handle WebSocket state changes."""
        try:
            # Get current state from the controller
            if self._led_controller:
                current_data = await self.hass.async_add_executor_job(self._led_controller.get_info)
                
                # Update the coordinator's data
                self.data = current_data
                
                # Notify all listeners (entities) of the update
                self.async_update_listeners()
                
                _LOGGER.debug("WebSocket change triggered HA update")
                
        except Exception as ex:
            _LOGGER.debug("Failed to handle WebSocket change: %s", ex)

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
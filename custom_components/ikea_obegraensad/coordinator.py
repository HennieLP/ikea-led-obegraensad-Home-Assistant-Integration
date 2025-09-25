"""Data update coordinator for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class IkeaLedCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the IKEA OBEGRÄNSAD LED device."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize."""
        self.host = host
        self._led_controller = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )

    async def _async_setup_controller(self) -> None:
        """Set up the LED controller."""
        if self._led_controller is None:
            try:
                # Import the library dynamically to avoid import issues
                import ikea_led_obegraensad_python_control
                
                self._led_controller = ikea_led_obegraensad_python_control.setup(self.host)
            except Exception as ex:
                _LOGGER.exception("Failed to set up IKEA LED controller")
                raise UpdateFailed(f"Error setting up controller: {ex}") from ex

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        await self._async_setup_controller()
        
        try:
            # Run the synchronous get_info method in executor
            info = await self.hass.async_add_executor_job(self._led_controller.get_info)
            return info
        except Exception as ex:
            _LOGGER.exception("Error fetching data from IKEA LED device")
            raise UpdateFailed(f"Error communicating with device at {self.host}: {ex}") from ex

    @property
    def led_controller(self):
        """Return the LED controller."""
        return self._led_controller
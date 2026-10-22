"""Data update coordinator for IKEA OBEGRÄNSAD LED Control."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Keys of the device's info message that the entities use
STATE_KEYS = ("brightness", "rotation", "plugin", "scheduleActive", "schedule", "plugins")

HTTP_TIMEOUT = aiohttp.ClientTimeout(total=10)
WS_HEARTBEAT = 30  # seconds; also detects a device that dropped off the network
WS_RECONNECT_DELAY = 5  # seconds


class IkeaLedCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Keep the device state in sync over its WebSocket, with HTTP as a fallback.

    Everything runs on Home Assistant's own event loop: the WebSocket is an
    aiohttp connection from HA's shared session, read by a background task and
    written to directly by the entities. (The previous version ran the socket in
    its own thread and event loop and sent commands from yet another loop, which
    asyncio does not support and which broke control on some installs.)
    """

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, host: str, config_entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            # Only a fallback; the WebSocket pushes every change
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )
        self.host = host
        self.base_url = f"http://{host}/api"
        self.ws_url = f"http://{host}/ws"
        self._session = async_get_clientsession(hass)
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._ws_task: asyncio.Task[None] | None = None

    @property
    def ws_connected(self) -> bool:
        """Return whether the WebSocket is currently open."""
        return self._ws is not None and not self._ws.closed

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the full state over HTTP (first refresh and fallback polling)."""
        try:
            async with self._session.get(
                f"{self.base_url}/info", timeout=HTTP_TIMEOUT
            ) as response:
                response.raise_for_status()
                info = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as ex:
            raise UpdateFailed(f"Error communicating with device at {self.host}: {ex}") from ex

        if not isinstance(info, dict):
            raise UpdateFailed(f"Unexpected response from device at {self.host}: {info!r}")
        return {**(self.data or {}), **_pick_state(info)}

    # WebSocket

    def async_start_websocket(self) -> None:
        """Start the background task that keeps the WebSocket open."""
        if self._ws_task is None:
            self._ws_task = self.config_entry.async_create_background_task(
                self.hass, self._websocket_loop(), f"{DOMAIN} websocket {self.host}"
            )

    async def _websocket_loop(self) -> None:
        """Connect, read messages until the socket drops, then reconnect."""
        while True:
            try:
                async with self._session.ws_connect(self.ws_url, heartbeat=WS_HEARTBEAT) as ws:
                    self._ws = ws
                    _LOGGER.debug("WebSocket connected to %s", self.ws_url)
                    async for message in ws:
                        if message.type in (aiohttp.WSMsgType.TEXT, aiohttp.WSMsgType.BINARY):
                            self._handle_ws_message(message.data)
                        elif message.type == aiohttp.WSMsgType.ERROR:
                            _LOGGER.debug("WebSocket error: %s", ws.exception())
                            break
            except (aiohttp.ClientError, TimeoutError) as ex:
                _LOGGER.debug("WebSocket connection to %s failed: %s", self.ws_url, ex)
            except Exception:  # noqa: BLE001 - keep reconnecting whatever went wrong
                _LOGGER.exception("Unexpected error in the WebSocket loop for %s", self.ws_url)
            finally:
                self._ws = None

            _LOGGER.debug("WebSocket to %s closed, reconnecting in %ss", self.ws_url, WS_RECONNECT_DELAY)
            await asyncio.sleep(WS_RECONNECT_DELAY)

    def _handle_ws_message(self, message: str | bytes) -> None:
        """Merge the state fields of an incoming message into the coordinator data."""
        try:
            data = json.loads(message)
        except ValueError:
            # The device can also send non-JSON frames; they carry no state
            _LOGGER.debug("Ignoring non-JSON WebSocket message")
            return
        if not isinstance(data, dict):
            return

        updates = _pick_state(data)
        if not updates:
            return
        new_data = {**(self.data or {}), **updates}
        if new_data != self.data:
            self.async_set_updated_data(new_data)

    async def _async_send_ws(self, payload: dict[str, Any]) -> bool:
        """Send a command over the WebSocket; return False when it is not open."""
        ws = self._ws
        if ws is None or ws.closed:
            return False
        try:
            await ws.send_json(payload)
        except (aiohttp.ClientError, ConnectionError) as ex:
            _LOGGER.debug("Sending %s over the WebSocket failed: %s", payload, ex)
            return False
        return True

    async def _async_http(self, method: str, path: str, params: dict[str, Any] | None = None) -> None:
        """Call one of the device's HTTP endpoints."""
        try:
            async with self._session.request(
                method, f"{self.base_url}/{path}", params=params, timeout=HTTP_TIMEOUT
            ) as response:
                if response.status == 404 and path.startswith("schedule/"):
                    raise HomeAssistantError(
                        "The device has no schedule; set one up in its web interface first"
                    )
                response.raise_for_status()
        except (aiohttp.ClientError, TimeoutError) as ex:
            raise HomeAssistantError(f"Could not reach the device at {self.host}: {ex}") from ex

    # LED control

    async def async_set_brightness(self, brightness: int) -> None:
        """Set the brightness value (0-255)."""
        if not 0 <= brightness <= 255:
            raise ValueError("Brightness must be between 0 and 255")
        if not await self._async_send_ws({"event": "brightness", "brightness": brightness}):
            await self._async_http("PATCH", "brightness", {"value": brightness})
            await self.async_request_refresh()

    async def async_set_plugin(self, plugin_id: int) -> None:
        """Set the active plugin."""
        if not await self._async_send_ws({"event": "plugin", "plugin": plugin_id}):
            await self._async_http("PATCH", "plugin", {"id": plugin_id})
            await self.async_request_refresh()

    async def async_rotate(self, direction: str = "right") -> None:
        """Rotate the display by 90° ('left' or 'right')."""
        if direction not in ("left", "right"):
            raise ValueError("Direction must be either 'left' or 'right'")
        # The firmware only offers rotation over the WebSocket
        if not await self._async_send_ws({"event": "rotate", "direction": direction}):
            raise HomeAssistantError(
                f"Cannot rotate: the WebSocket to {self.host} is not connected"
            )

    async def async_set_schedule_active(self, active: bool) -> None:
        """Start or stop the schedule stored on the device."""
        # The firmware only offers this over HTTP
        await self._async_http("GET", "schedule/start" if active else "schedule/stop")
        if not self.ws_connected:
            await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Stop the WebSocket task and close the connection."""
        if self._ws_task is not None:
            self._ws_task.cancel()
            self._ws_task = None
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
        await super().async_shutdown()


def _pick_state(data: dict[str, Any]) -> dict[str, Any]:
    """Return only the state fields of a device message."""
    return {key: data[key] for key in STATE_KEYS if key in data}

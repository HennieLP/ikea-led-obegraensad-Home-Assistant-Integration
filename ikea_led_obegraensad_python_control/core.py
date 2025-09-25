import requests
import websockets
import asyncio
import json
import time
from typing import Optional, Dict, Any
import threading

class IkeaLedObegraensad:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.base_url = f"http://{self.ip_address}/api"
        self.ws_url = f"ws://{self.ip_address}/ws"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.ws_connected = False
        self._state = {
            "brightness": 0,
            "rotation": 0,
            "plugin": None,
            "scheduleActive": False,
            "schedule": [],
            "plugins": []
        }
        self._ws_lock = threading.Lock()
        self._last_state = {}
        self._start_websocket()
        self._start_monitoring()

    def _start_websocket(self):
        """Start the WebSocket connection in a background thread"""
        def run_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._websocket_loop())
        
        self._ws_thread = threading.Thread(target=run_async_loop, daemon=True)
        self._ws_thread.start()

    def _start_monitoring(self):
        """Start the state monitoring in a background thread"""
        def monitor_changes():
            while True:
                try:
                    with self._ws_lock:
                        current_state = dict(self._state)
                    
                    # Check for changes and log them
                    for key, value in current_state.items():
                        if key not in self._last_state or self._last_state[key] != value:
                            if key in self._last_state:  # Don't log initial values
                                print(f"Change detected: {key} changed from {self._last_state[key]} to {value}")
                            self._last_state[key] = value
                    
                    time.sleep(0.5)  # Check every 500ms
                except Exception as e:
                    # Silently continue if there's an error getting state
                    time.sleep(1)
        
        self._monitor_thread = threading.Thread(target=monitor_changes, daemon=True)
        self._monitor_thread.start()

    async def _websocket_loop(self):
        """Main WebSocket connection loop"""
        while True:
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    self.websocket = websocket
                    self.ws_connected = True
                    
                    while True:
                        try:
                            message = await websocket.recv()
                            await self._handle_ws_message(message)
                        except websockets.ConnectionClosed:
                            break
            except Exception as e:
                print(f"WebSocket connection error: {e}")
            finally:
                self.ws_connected = False
                self.websocket = None
            
            # Wait before reconnecting
            await asyncio.sleep(5)

    async def _handle_ws_message(self, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            with self._ws_lock:
                if "brightness" in data:
                    self._state["brightness"] = data["brightness"]
                if "rotation" in data:
                    self._state["rotation"] = data["rotation"]
                if "plugin" in data:
                    self._state["plugin"] = data["plugin"]
                if "scheduleActive" in data:
                    self._state["scheduleActive"] = data["scheduleActive"]
                if "schedule" in data:
                    self._state["schedule"] = data["schedule"]
                if "plugins" in data:
                    self._state["plugins"] = data["plugins"]
        except json.JSONDecodeError as e:
            print(f"Error parsing WebSocket message: {e}")

    async def _send_ws_message(self, data: Dict[str, Any]):
        """Send a message through the WebSocket connection"""
        if not self.ws_connected or not self.websocket:
            return
        
        try:
            await self.websocket.send(json.dumps(data))
        except websockets.ConnectionClosed:
            print("WebSocket connection closed while sending message")
            self.ws_connected = False
        except Exception as e:
            print(f"Error sending WebSocket message: {e}")
            # Don't set ws_connected to False for other errors as connection might still be valid

    def _send_request(self, endpoint, method="GET", data=None):
        url = f"{self.base_url}/{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "PATCH":
            response = requests.patch(url)
        else:
            raise ValueError("Unsupported HTTP method")
        
        response.raise_for_status()
        return response.json()

    def _connect_ws(self) -> None:
        """Attempt to reconnect the WebSocket connection"""
        if not self.ws_connected:
            # Only restart if the existing thread is not alive
            if not hasattr(self, '_ws_thread') or not self._ws_thread.is_alive():
                # Start a new websocket connection
                self._start_websocket()
            
            # Wait briefly for connection to establish, but don't block too long
            for _ in range(5):  # Try for up to 0.5 seconds
                if self.ws_connected:
                    break
                time.sleep(0.1)

    def _send_ws_command(self, data: Dict[str, Any]) -> None:
        """Helper method to send WebSocket commands"""
        if not self.ws_connected:
            # Try reconnecting
            self._connect_ws()
        
        # If still not connected, raise an error since the command cannot be executed
        if not self.ws_connected:
            raise ConnectionError("WebSocket connection is not available and reconnection failed")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._send_ws_message(data))
        except Exception as e:
            print(f"Failed to send WebSocket command: {e}")
            raise
        finally:
            loop.close()

    def turn_on(self):
        """Turn on the LED display (set brightness to maximum)"""
        return self.set_brightness(255)

    def turn_off(self):
        """Turn off the LED display (set brightness to 0)"""
        return self.set_brightness(0)

    def set_brightness(self, brightness: int) -> None:
        """Set the brightness value (0-255)"""
        if not (0 <= brightness <= 255):
            raise ValueError("Brightness must be between 0 and 255")
        
        self._send_ws_command({
            "event": "brightness",
            "brightness": brightness
        })
        
    def get_brightness(self) -> int:
        """Get the current brightness value (0-255)"""
        with self._ws_lock:
            return self._state["brightness"]

    def get_rotation(self) -> int:
        """Get the current rotation value (0-3)"""
        with self._ws_lock:
            return self._state["rotation"]

    def get_active_plugin(self) -> Optional[str]:
        """Get the currently active plugin ID"""
        with self._ws_lock:
            return self._state["plugin"]

    def get_available_plugins(self) -> list:
        """Get list of available plugins"""
        with self._ws_lock:
            return self._state["plugins"]

    def get_schedule_state(self) -> bool:
        """Get whether the schedule is active"""
        with self._ws_lock:
            return self._state["scheduleActive"]

    def get_schedule(self) -> list:
        """Get the current schedule"""
        with self._ws_lock:
            return self._state["schedule"]

    def get_info(self) -> dict:
        """Get all current state information"""
        with self._ws_lock:
            return dict(self._state)

    def set_plugin(self, plugin_id: int) -> None:
        """Set the active plugin"""
        self._send_ws_command({
            "event": "plugin",
            "plugin": plugin_id
        })
    
    def set_rotation(self, direction: str) -> None:
        """Rotate the display (direction should be 'left' or 'right')"""
        if direction not in ['left', 'right']:
            raise ValueError("Direction must be either 'left' or 'right'")
        
        self._send_ws_command({
            "event": "rotate",
            "direction": direction
        })
        

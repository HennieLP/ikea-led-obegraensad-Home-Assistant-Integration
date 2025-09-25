import requests

class IkeaLedObegraensad:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.base_url = f"http://{self.ip_address}/api"

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

    def turn_on(self):
        return self.set_brightness(255)

    def turn_off(self):
        return self.set_brightness(0)

    def set_brightness(self, brightness):
        if not (0 <= brightness <= 255):
            raise ValueError("Brightness must be between 0 and 255")
        return self._send_request(f"brightness?value={brightness}", method="PATCH")
    
    def get_brightness(self):
        return 0

    def get_info(self):
        return self._send_request("info")
    
    def set_plugin(self, plugin_id):
        return self._send_request(f"plugin?id={plugin_id}", method="PATCH")
    
    def turn_on_schedule(self):
        return self._send_request("schedule/start", method="PATCH")

    def turn_off_schedule(self):
        return self._send_request("schedule/stop", method="PATCH")
    
    def get_schedule_state(self):
        return self.get_info().get("schedule", {}).get("state", "unknown")
        

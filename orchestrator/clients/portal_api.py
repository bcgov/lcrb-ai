# portal_api.py
import json, requests

class PortalApi:
    def __init__(self, base_url, token_provider, timeout=20.0):
        self.base_url = base_url.rstrip("/")
        self.token_provider = token_provider
        self.timeout = timeout

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token_provider()}",
            "Content-Type": "application/json"
        }

    def create_application(self, app_type_name: str) -> str:
        url = f"{self.base_url}/api/applications?format=minimal"
        payload = {
            "ApplicationType": {"Name": app_type_name}
        }
        r = requests.post(url, headers=self._headers(), data=json.dumps(payload), timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        return data["id"]   # GUID from ApplicationsController

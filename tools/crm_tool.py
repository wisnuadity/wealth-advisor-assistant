import requests


class CRMTool:
    """Abstraction layer for retrieving client profiles from the CRM API."""

    def __init__(self, base_url="http://127.0.0.1:5000", timeout=5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_client_profile(self, client_id):
        """Fetch a client profile or raise a clear error."""
        url = f"{self.base_url}/clients/{client_id}"

        try:
            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 404:
                raise ValueError(f"Client '{client_id}' was not found in CRM.")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Unable to retrieve CRM profile for '{client_id}'."
            ) from exc

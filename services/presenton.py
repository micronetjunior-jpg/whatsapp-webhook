import requests
from config import PRESENTON_INTERNAL_URL, PRESENTON_PUBLIC_URL

class PresentonClient:
    def create(self, payload):
        r = requests.post(
            f"{PRESENTON_INTERNAL_URL}/api/v1/ppt/presentation/generate",
            json=payload,
            timeout=300
        )
        r.raise_for_status()
        return r.json()

    def edit_url(self, path):
        return f"{PRESENTON_PUBLIC_URL}{path}"
import requests
from config import KOKOROURL

def text_to_speech(texto):
    r = requests.post(
        f"{KOKOROURL}/v1/audio/speech",
        json={"model": "kokoro", "input": texto},
        timeout=60
    )
    r.raise_for_status()
    return r.content
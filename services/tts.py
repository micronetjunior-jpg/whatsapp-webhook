import requests
from config import KOKOROURL

def text_to_speech(texto):
    payload = {
        "model": "kokoro",
        "input": texto,
        "voice": "af_heart",
        "response_format": "mp3",
        "download_format": "mp3",
        "speed": 1,
        "stream": False,  # 👈 importante
        "return_download_link": False,
        "lang_code": "es",
        "volume_multiplier": 1,
        "normalization_options": {
            "normalize": True,
            "unit_normalization": False,
            "url_normalization": True,
            "email_normalization": True,
            "optional_pluralization_normalization": True,
            "phone_normalization": True,
            "replace_remaining_symbols": True
        }
    }
    response = requests.post(
        f"{KOKOROURL}/v1/audio/speech",
        json=payload,
        timeout=60
    )
    response.raise_for_status()
    return response.content
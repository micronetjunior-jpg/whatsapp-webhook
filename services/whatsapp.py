import requests
from config import WHATSAPP_TOKEN, PHONE_NUMBER_ID

BASE_URL = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}"

def send_text(to, text):
    requests.post(
        f"{BASE_URL}/messages",
        headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": text}
        }
    )

def upload_media(file_bytes, mime, filename):
    r = requests.post(
        f"{BASE_URL}/media",
        headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
        files={
            "file": (filename, file_bytes, mime),
            "messaging_product": (None, "whatsapp")
        }
    )
    r.raise_for_status()
    return r.json()["id"]

def send_audio(to, media_id):
    requests.post(
        f"{BASE_URL}/messages",
        headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "audio",
            "audio": {"id": media_id}
        }
    )

def subir_audio_ruta(ruta_audio: str) -> str:
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/media"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    files = {
        "file": (
            "audio.mp3",
            open(ruta_audio, "rb"),
            "audio/mpeg"
        )
    }
    data = {"messaging_product": "whatsapp"}
    response = requests.post(
        url,
        headers=headers,
        files=files,
        data=data
    )
    response.raise_for_status()
    media_id = response.json()["id"]
    return media_id # media_id

def download_media(media_id):
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    url = requests.get(
        f"https://graph.facebook.com/v24.0/{media_id}",
        headers=headers
    ).json()["url"]
    return requests.get(url, headers=headers).content
    
def send_template(to,name,lang):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    payload = {
        "messaging_product":"whatsapp",
        "to":to,
        "type":"template",
        "template":{"name":name,"language":{"code":"es"}}
    }
    response = requests.post(url, headers=headers, json=payload)

def subir_pdf(pdf_bytes: bytes) -> str:
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/media"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

    files = {
        "file": ("respuesta.pdf", pdf_bytes, "application/pdf"),
        "type": (None, "application/pdf"),
        "messaging_product": (None, "whatsapp")
    }
    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json()["id"]
    
def enviar_pdf(to: str, media_id: str):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "document",
        "document": {
            "id": media_id,
            "filename": "respuesta.pdf"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    



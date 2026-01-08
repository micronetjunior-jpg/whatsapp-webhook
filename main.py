from fastapi import FastAPI, Request
import os
import requests

app = FastAPI()

VERIFY_TOKEN = "mi_token"
META_TOKEN = os.getenv("META_TOKEN")
RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WABA_ID = os.getenv("WABA_ID")

print("repo cloud")

@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    return {"error":"token invalido"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("📩 ENTRANTE:", data)

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]

        print(f"Mensaje de {from_number}: {text}")

        send_message(from_number, "Hola 👋")

    except Exception as e:
        print("No es un mensaje de texto:", e)

    return {"ok": True}


def send_message(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }

    r = requests.post(url, json=payload, headers=headers)
    print("📤 RESPUESTA META:", r.status_code, r.text)

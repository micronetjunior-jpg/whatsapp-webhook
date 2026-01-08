from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
import os
import requests

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
META_TOKEN = os.getenv("META_TOKEN")
RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WABA_ID = os.getenv("WABA_ID")

print(RAILWAY_TOKEN)

print("repo cloud")

@app.get("/webhook", response_class=PlainTextResponse)
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    challenge: str = Query(..., alias="hub.challenge"),
    verify_token: str = Query(..., alias="hub.verify_token"),
    mensaje: str = Query(..., alias="hub.mensaje")
):
    print("mensaje:",mensaje)
    print("get")
    print("modo:",mode)
    print("challenge:",challenge)
    print("token real",VERIFY_TOKEN)
    print("token ingresado",verify_token)
    if mode == "subscribe" and verify_token == VERIFY_TOKEN:
        print("suscrito")
        return mensaje
    return {"error":"token invalido"}

@app.post("/webhook")
async def webhook(request: Request):
    print("post")
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
    print("eco")
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": "573176429931",
        "text": {"body": "respuesta"}
    }

    r = requests.post(url, json=payload, headers=headers)
    print("📤 RESPUESTA META:", r.status_code, r.text)

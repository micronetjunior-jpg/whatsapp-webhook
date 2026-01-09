from fastapi import FastAPI, Request, Query, Response
from fastapi.responses import PlainTextResponse
import os
import requests
import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
META_TOKEN = os.getenv("META_TOKEN")
RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WABA_ID = os.getenv("WABA_ID")

"""
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

    
"""
    
# -------------------------------
# VERIFICACIÓN DEL WEBHOOK (GET)
# -------------------------------
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)

    return Response(status_code=403)

# -------------------------------
# RECEPCIÓN DE MENSAJES (POST)
# -------------------------------
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    print("📩 Evento recibido de Meta:")
    print(data)

    try:
        entry = data["entry"][0]
        change = entry["changes"][0]
        value = change["value"]

        messages = value.get("messages")
        if not messages:
            return Response(status_code=200)

        message = messages[0]
        from_number = message["from"]
        text = message["text"]["body"]

        print(f"📨 Mensaje de {from_number}: {text}")

        # Procesamiento
        reply_text = procesar_mensaje(text)

        # Responder
        print("Se procede a remitir respuesta a",from_number)
        enviar_mensaje(from_number,reply_text)

    except Exception as e:
        print("❌ Error procesando mensaje:", e)

    # Meta necesita 200 SIEMPRE
    return Response(status_code=200)


# -------------------------------
# LÓGICA DEL MENSAJE
# -------------------------------
def procesar_mensaje(texto: str) -> str:
    texto = texto.lower()

    if "hola" in texto:
        return "Hola 👋 ¿Cómo puedo ayudarte?"
    if "info" in texto:
        return "Te puedo contar sobre nuestros programas educativos 🤖📚"

    return "Mensaje recibido ✅"


# -------------------------------
# ENVÍO DE RESPUESTAS A WHATSAPP
# -------------------------------
def enviar_mensaje(to: str, message: str):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"
    
    print(url)

    headers = {
        "Authorization":f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type":"application/json"
    }
    
    print(headers)

    payload = {
        "messaging_product":"whatsapp",
        "to":to,
        "text":{"body":message}
    }
    
    print(payload)

    response = requests.post(url, headers=headers, json=payload)

    print("📤 Respuesta enviada:", response.status_code, response.text)
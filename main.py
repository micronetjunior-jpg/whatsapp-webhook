from fastapi import FastAPI, Request, Query, Response
from fastapi.responses import PlainTextResponse
import openai
import os
import requests

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
META_TOKEN = os.getenv("META_TOKEN")
RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WABA_ID = os.getenv("WABA_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")


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

    try:
    
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # 📨 MENSAJE DEL USUARIO
        if "messages" in value:
            messages = value["messages"][0]
            print("payload",messages)

        # 📬 STATUS (delivered, read, etc.)
        elif "statuses" in value:
            statuses = value["statuses"]
            print("STATUS:", statuses)
        else:
            print("Evento no reconocido")

        # Procesamiento
        reply_text = procesar_mensaje(messages)
        #print(reply_text)

        from_number=messages["from"]
        text=messages["text"]["body"]
        
        print(f"📨 Mensaje de {from_number}: {text}")

        # Responder
        print("Se procede a remitir respuesta a",from_number)
        #enviar_mensaje(from_number,reply_text)

    except Exception as e:
        print("❌ Error procesando mensaje:", e)

    # Meta necesita 200 SIEMPRE
    return Response(status_code=200)


# -------------------------------
# LÓGICA DEL MENSAJE
# -------------------------------
def procesar_mensaje(texto: list) -> list:
    saludo = ["hola", "buenas", "como estas", "buenas tardes"]
    
    #texto_lower = texto[0]["text"]["body"].lower()#para dict
    texto_lower = texto.get("text", {}).get("body").lower()
    
    #print(texto_lower)
    
    # Detectar saludos
    if any(palabra in texto_lower for palabra in saludo):
        return "Hola 👋 ¿Cómo puedo ayudarte?"

    # Detectar si es una duda o pregunta
    palabras_duda = ["duda", "pregunta", "consulta", "no entiendo", "ayuda"]
    if any(palabra in texto_lower for palabra in palabras_duda):
        return procesarIA(texto_lower) # Solo procesa IA si es una duda

    # Si no es saludo ni duda, pedimos que escriba la pregunta completa
    return "Por favor, escribe tu duda o pregunta completa para poder ayudarte."

# -------------------------------
# PROCESAMIETO CON IA
# -------------------------------




# Asegúrate de tener la variable de entorno OPENAI_API_KEY configurada
openai.api_key = os.getenv("OPENAI_API_KEY")

def procesarIA(solicitud: str, modelo: str = "gpt-3.5-turbo") -> str:
    """
    Procesa un texto usando la API moderna de OpenAI ChatCompletion.
    """
    try:
        response = openai.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": solicitud}],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error procesando la solicitud: {e}"

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
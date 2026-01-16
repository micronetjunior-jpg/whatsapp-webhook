from fastapi import FastAPI, Request, Query, Response, UploadFile, File
from fastapi.responses import PlainTextResponse
import openai
import os
import requests
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
import redis
import json
from redis_client import r
r.set("test", "ok")

app = FastAPI() 

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
META_TOKEN = os.getenv("META_TOKEN")
RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WABA_ID = os.getenv("WABA_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDISHOST = os.getenv("REDISHOST")
REDISPORT = os.getenv("REDISPORT")
REDISPASSWORD = os.getenv("REDIS_PASAWORD")
KOKOROURL = os.getenv("KOKOROURL")
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
    print("datos:",data)
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # 📨 MENSAJE DEL USUARIO
        if "messages" in value:
            messages = value["messages"][0]
            print("payload",messages)
            telefono=messages["from"]
            tipo=messages["type"]
            print("tipo:",tipo)
            if tipo=="text":
                print("procesando respuesta")
                guardar_estado("tipo_respuesta","texto")
                text=messages["text"]["body"]
                # Procesamiento
                reply_text = procesar_mensaje(messages,telefono)
                #print(reply_text)
                print(f"📨 Mensaje de {telefono}: {text}")
                # Responder
            elif tipo=="audio":
                media_id = messages["audio"]["id"]
                print("media_id:",media_id)
                guardar_estado("tipo_respuesta","audio")
                estado = obtener_estado(telefono+"media_id")
                print("estado wait:",estado)
                if estado and estado["estado"] == media_id:
                    print("esperando para enviar audio")
                else:
                    audio_bytes = descargar_audio(media_id)
                    texto = transcribir_audio(audio_bytes)
                    transcrito = obtener_estado(telefono+"transcripcion")
                    print(transcrito)
                    if transcrito and transcrito["estado"] == texto:
                        print("CONTINUAR")
                    else:
                        guardar_estado(telefono+"transcripcion",texto)
                        print("texto:",texto)
                        # Ahora `texto` es como si el usuario lo hubiera escrito
                        procesar_mensaje(telefono=telefono,textoAudio=texto)
            elif tipo=="button":
                guardar_estado("tipo_respuesta","boton")
                res = messages["button"]["text"]
                reply_text = procesar_mensaje(telefono=telefono,textoRespuesta=res)
                print(f"📨 Mensaje de {telefono}: {res}")
            else:
                guardar_estado("tipo_respuesta","IDLE")
            
        # 📬 STATUS (delivered, read, etc.)
        elif "statuses" in value:
            statuses = value["statuses"]
            print("STATUS:", statuses)
        else:
            print("Evento no reconocido")

    except Exception as e:
        print("Try de metodo post ❌ Error procesando mensaje:", e)

    # Meta necesita 200 SIEMPRE
    return Response(status_code=200)


# -------------------------------
# LÓGICA DEL MENSAJE
# -------------------------------
def procesar_mensaje(texto=None,telefono=None,textoAudio = None, textoRespuesta=None) -> list:
    print("procesando mensaje")
    saludo = ["hola", "buenas", "como estas", "buenas tardes"]
    palabras_duda = ["duda", "pregunta", "consulta", "no entiendo", "ayuda","?","ayudame","ayúdame"]
    si_no = ["si","sí","si.","sí."]
    saludo_o_pregunta = ["saludo","pregunta","saludo.","pregunta."]
    
    if textoAudio != None:
        mensaje = textoAudio.lower()
    elif textoRespuesta != None:
        mensaje = textoRespuesta.lower()
    else:
        mensaje = texto.get("text", {}).get("body").lower()
        guardar_estado("tipo_respuesta","texto")
    
    verificar_pregunta = saludo_pregunta(mensaje).lower()
    print("tipo de mensaje:",verificar_pregunta)
    estado = obtener_estado(telefono)
    print("verificando si PDF")
    if estado and estado["estado"] == "ESPERANDO_CONFIRMACION_PDF":
    
        if mensaje.lower() in ["si", "sí", "s"]:
            texto = estado["data"]["texto"]
            
            
            pdf = generar_pdf_bytes(texto)
            media_id = subir_pdf_whatsapp(pdf)
            enviar_pdf_whatsapp(media_id, telefono)
            guardar_estado(telefono, "IDLE")
    
        elif mensaje.lower() in ["no", "n"]:
            enviar_mensaje(telefono, "Perfecto 👍")
            guardar_estado(telefono, "IDLE")
    
        else:
            enviar_mensaje(
                telefono,
                "Por favor responde SI o NO"
            )
    else:
        guardar_estado(telefono, "IDLE")
        #if any(palabra in verificar_pregunta for palabra in saludo_no):
            #procesarPregunta(mensaje,telefono)
        # Detectar saludos
        if mensaje.lower() in ["si","no"]:
            print("idle")
        elif verificar_pregunta in ["saludo","saludo."]:
            print("es un saludo")
            enviar_mensaje(telefono,"Bienvenido 👋 ¿Cómo puedo ayudarte? escribe o mándame una nota de voz")
        elif verificar_pregunta in ["pregunta","pregunta."]:
            print("es una pregunta")
            procesarPregunta(mensaje,telefono)
        elif any(palabra in mensaje for palabra in saludo):
            print("saludo")
            enviar_mensaje(telefono,"Hola 👋 ¿Cómo puedo ayudarte?")
        # Detectar si es una duda o pregunta
        elif any(palabra in mensaje for palabra in palabras_duda):
            procesarPregunta(mensaje,telefono)
        else:
        # Si no es saludo ni duda, pedimos que escriba la pregunta completa
            enviar_mensaje(telefono, "Por favor, escribe tu duda o pregunta completa para poder ayudarte.")

def procesarPregunta(mensaje: str, telefono: str):
    print("procesar IA")
    respuestaIA = procesarIA(telefono,mensaje)
    
    print("Se procede a remitir respuesta a",telefono)
    
    tipo = obtener_estado("tipo_respuesta")["estado"]
    print(tipo)

    if tipo == "audio":
        guardar_estado("tipo_respuesta", "IDLE")
        guardar_estado(telefono+"wait","enviando_audio")
        responder_con_audio(telefono,respuestaIA)
    else:
        enviar_mensaje(telefono,respuestaIA)
        
    if len(respuestaIA) > 1000:
        guardar_estado(
            telefono,
            "ESPERANDO_CONFIRMACION_PDF",
            {"texto": respuestaIA}
        )
        enviar_plantilla(
            telefono,
            "crearpdf"
        )
    guardar_estado(telefono+"wait","IDLE")
# -------------------------------
# PROCESAMIETO CON IA
# -------------------------------

openai.api_key = OPENAI_API_KEY
print(OPENAI_API_KEY)

def procesarIA(telefono: str, solicitud: str, modelo: str = "gpt-4o-mini") -> str:
    """
    Procesa un texto usando la API moderna de OpenAI ChatCompletion.
    """
    print("solicitud:",solicitud)
    try:
        print("vamo al openIA")
        
        historial = obtener_historial(telefono)
        
        if not historial:
            historial.append({
                "role": "system",
                "content": "Eres un asistente de IA."
            })

        historial.append({"role": "user", "content": solicitud})
        
        response = openai.chat.completions.create(
            model=modelo,
            #messages=[
            #{"role": "user", "content": solicitud}
            #],
            messages=historial,
            max_tokens=1000,
            temperature=0.5
        )
        respuesta = response.choices[0].message.content
        print("num caracteres:",len(respuesta))
        historial.append({"role": "assistant", "content": respuesta})
        guardar_historial(telefono, historial)
        print("respuesta:",respuesta)
        return respuesta
    except Exception as e:
        print("error en try de OpenAI")
        return f"Try openAI, Error procesando la solicitud: {e}"

def saludo_pregunta(pregunta: str, modelo: str = "gpt-4o-mini") -> str:
    try:
        response = openai.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": "¿El siguiente texto es un saludo o una pregunta? "+pregunta+" Solo responde saludo o pregunta"}],
            max_tokens=1000,
            temperature=0.7
        )
        respuesta = response.choices[0].message.content
        print("respuesta:",respuesta)
        return respuesta
    except Exception as e:
        print("error en try de OpenAI")
        return f"Try openAI, Error procesando la solicitud: {e}"

def enviar_mensaje(to: str, message: str):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization":f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type":"application/json"
    }
    payload = {
        "messaging_product":"whatsapp",
        "to":to,
        "text":{"body":message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("📤 Respuesta enviada:", response.status_code, response.text)

def enviar_plantilla(to: str, nombre: str):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization":f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type":"application/json"
    }
    payload = {
        "messaging_product":"whatsapp",
        "to":to,
        "type":"template",
        "template":{"name":nombre,"language":{"code":"es"}}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("📤 Respuesta enviada:", response.status_code, response.text)

def generar_pdf_bytes(texto: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()

    texto = texto.replace("\n", "<br/>")
    doc.build([Paragraph(texto, styles["Normal"])])

    buffer.seek(0)
    return buffer.read()

def subir_pdf_whatsapp(pdf_bytes: bytes) -> str:
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/media"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}"
    }

    files = {
        "file": ("respuesta.pdf", pdf_bytes, "application/pdf"),
        "type": (None, "application/pdf"),
        "messaging_product": (None, "whatsapp")
    }

    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()

    return response.json()["id"]
    
def enviar_pdf_whatsapp(media_id: str, to: str):
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
    
def guardar_estado(telefono, estado, data=None, ttl=300):
    payload = {
        "estado": estado,
        "data": data
    }
    r.setex(f"user:{telefono}", ttl, json.dumps(payload))
    
def obtener_estado(telefono):
    data = r.get(f"user:{telefono}")
    return json.loads(data) if data else None

def descargar_audio(media_id):
    # 1. Obtener URL del media
    url = f"https://graph.facebook.com/v24.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    media_url = r.json()["url"]

    # 2. Descargar el audio
    audio_response = requests.get(media_url, headers=headers)
    audio_response.raise_for_status()

    return audio_response.content
    
from openai import OpenAI
import tempfile

client = OpenAI()

def transcribir_audio(audio_bytes: bytes) -> str:
    # Whisper necesita un archivo
    with tempfile.NamedTemporaryFile(suffix=".ogg") as f:
        f.write(audio_bytes)
        f.flush()

        transcription = client.audio.transcriptions.create(
            file=open(f.name, "rb"),
            model="gpt-4o-mini-transcribe"
        )

    return transcription.text
    

def kokoro_tts(texto: str) -> bytes:
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

    return response.content  # 👈 bytes MP3

def generar_audio_mp3(texto: str) -> str:
    audio_bytes = kokoro_tts(texto)

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    ) as f:
        f.write(audio_bytes)
        return f.name

def subir_audio_whatsapp(ruta_audio: str) -> str:
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/media"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}"
    }

    files = {
        "file": (
            "audio.mp3",
            open(ruta_audio, "rb"),
            "audio/mpeg"
        )
    }

    data = {
        "messaging_product": "whatsapp"
    }

    response = requests.post(
        url,
        headers=headers,
        files=files,
        data=data
    )

    response.raise_for_status()
    media_id = response.json()["id"]
    return media_id # media_id
    
def enviar_audio_whatsapp(telefono: str, media_id: str):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "audio",
        "audio": {
            "id": media_id
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    response.raise_for_status()
    
def responder_con_audio(telefono: str, texto: str):
    ruta_audio = generar_audio_mp3(texto)
    media_id = subir_audio_whatsapp(ruta_audio)
    guardar_estado(telefono+"media_id",media_id)
    enviar_audio_whatsapp(telefono, media_id)
    
import json

def guardar_historial(telefono, mensajes):
    r.set(
        f"chat:{telefono}",
        json.dumps(mensajes),
        ex=3600  # 1 hora
    )

def obtener_historial(telefono):
    data = r.get(f"chat:{telefono}")
    return json.loads(data) if data else []





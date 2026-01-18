from memory import *
from services.whatsapp import *
from services.ai import *
from services.pdf import *
from services.tts import *

def isBusy(to):
    key = to+"busy"
    if get_event(key) and get_event(key)["status"] == "busy":
        return True
    else:
        return False
        
def setBusy(to,state):
    key = to+"busy"
    set_event(key,state)

def extract_message(payload: dict) -> dict | None:
    try:
        return payload["entry"][0]["changes"][0]["value"]["messages"][0]
    except (KeyError, IndexError, TypeError):
        return None

async def handle_message(data):
    msg = extract_message(data)
    if not msg:
        return
    
    telefono = msg["from"]

    if not acquire_user_lock(telefono):
        send_text(telefono, "⏳ Estoy procesando tu solicitud anterior")
        return

    try:
        if isBusy(telefono):
            return
        if msg["type"] == "text":
            respuesta = ask_ai(telefono, msg["text"]["body"])
            send_text(telefono, respuesta)
            if len(respuesta) > 1073:
                set_event("pdf","generar")
                set_event("respuesta",respuesta)
                send_template(telefono,"crearpdf","es")
        if msg["type"] == "button":
            respuesta = msg["button"]["text"]
            if get_event("pdf")["status"] == "generar":
                if respuesta.lower() in ["si","sí","s"]:
                    setBusy(telefono,True)
                    send_text(telefono, "generando pdf")
                    buffer = generar_pdf(get_event("respuesta")["status"])
                    media_id = subir_pdf(buffer)
                    enviar_pdf(telefono,media_id)
                    set_event("pdf","")
                    set_event("respuesta","")
                    setBusy(telefono,False)
                else:
                    set_event("respuesta","")
        elif msg["type"] == "audio":
            media_id = msg["audio"]["id"]
            if get_event(media_id):
                return
            setBusy(telefono,True)
            set_event(media_id, "PROCESSING")
            send_text
            audio = download_media(media_id)
            texto = transcribir_audio(audio)
            respuesta = ask_ai(telefono, texto)
            audio_path = generar_audio_mp3(respuesta)
            #media_id_sent = subir_audio_ruta(audio_path)
            #enviar_audio(telefono, media_id_sent)
            if len(respuesta) > 1073:
                set_event("pdf","generar")
                set_event("respuesta",respuesta)
                send_template(telefono,"crearpdf","es")
            set_event(media_id, "DONE")
            setBusy(telefono,False)
    finally:
        release_user_lock(telefono)
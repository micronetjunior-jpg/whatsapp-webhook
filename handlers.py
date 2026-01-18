from memory import *
from services.whatsapp import *
from services.ai import *
from services.pdf import *
from services.tts import *

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
        if get_event("busy") == "YES":
            return
        if msg["type"] == "text":
            respuesta = ask_ai(telefono, msg["text"]["body"])
            send_text(telefono, respuesta)
            if len(respuesta) > 1073:
                send_template(telefono,"crearpdf","es")
        if msg["type"] == "button":
            respuesta = msg["button"]["text"]
            print(respuesta)
            if get_event("pdf") == "generar":
                if respuesta.lower() in ["si","sí","s"]:
                    set_event("busy","YES")
                    send_text(telefono, "generando pdf")
                    buffer = generar_pdf(get_event("respuesta"))
                    media_id = subir_pdf(buffer)
                    enviar_pdf(telefono,media_id)
                    set_event("busy", "IDLE")
                    set_event("pdf","")
                    set_event("respuesta","")
                else:
                    set_event("respuesta","")
        elif msg["type"] == "audio":
            media_id = msg["audio"]["id"]
            if get_event(media_id):
                return
            set_event(media_id, "PROCESSING")
            audio = download_media(media_id)
            texto = transcribir_audio(audio)
            respuesta = ask_ai(telefono, texto)
            audio_path = generar_audio_mp3(respuesta)
            media_id_sent = subir_audio_ruta(audio_path)
            send_audio(telefono, media_id_sent)
            if len(respuesta) > 1073:
                send_template(telefono,"crearpdf","es")
                set_event("pdf","generar")
                set_event("respuesta",respuesta)
            set_event(media_id, "DONE")
    finally:
        release_user_lock(telefono)
from memory import *
from services.whatsapp import *
from services.ai import *
from services.pdf import *
from services.tts import *

async def handle_message(data):
    msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
    
    print("data",data["entry"][0]["changes"][0])
    print("MSG:",msg)
    
    telefono = msg["from"]

    if not acquire_user_lock(telefono):
        send_text(telefono, "⏳ Estoy procesando tu solicitud anterior")
        return

    try:
        if msg["type"] == "text":
            respuesta = ask_ai(telefono, msg["text"]["body"])
            send_text(telefono, respuesta)

        if msg["type"] == "audio":
            media_id = msg["audio"]["id"]
            if get_event(media_id):
                return

            set_event(media_id, "PROCESSING")
            audio = download_media(media_id)
            texto = transcribir_audio(audio)
            respuesta = ask_ai(telefono, texto)
            audio_res = text_to_speech(respuesta)
            mime = "application/octet-stream"
            media_id = upload_media(audio_res,",mime, "audio_respuesta")
            send_audio(telefono, media_id)
            set_event(media_id, "DONE")
    finally:
        release_user_lock(telefono)
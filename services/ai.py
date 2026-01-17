import openai
from config import OPENAI_API_KEY
from memory import obtener_historial, guardar_historial

openai.api_key = OPENAI_API_KEY

def ask_ai(telefono, texto):
    historial = obtener_historial(telefono)
    if not historial:
        historial = [{"role": "system", "content": "Eres un asistente útil. Genera las respuestas sin pies de página, los encabezados, asteriscos o signos"}]

    historial.append({"role": "user", "content": texto})

    res = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=historial,
        max_tokens=1000
    )

    respuesta = res.choices[0].message.content
    historial.append({"role": "assistant", "content": respuesta})
    guardar_historial(telefono, historial)
    return respuesta
    
    
from openai import OpenAI
import tempfile
client = OpenAI(api_key=OPENAI_API_KEY)
def transcribir_audio(audio_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".ogg") as f:
        f.write(audio_bytes)
        f.flush()

        transcription = client.audio.transcriptions.create(
            file=open(f.name, "rb"),
            model="gpt-4o-mini-transcribe"
        )

    return transcription.text
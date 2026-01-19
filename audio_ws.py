import json
import websockets
from fastapi import FastAPI, WebSocket
from config import OPENAI_API_KEY

appWS = FastAPI()

@appWS.websocket("/audio")
async def audio_bridge(ws: WebSocket):
    await ws.accept()
    print("🔗 Meta conectado al audio WS")

    # Conexión a OpenAI Realtime
    async with websockets.connect(
        "wss://api.openai.com/v1/realtime?model=gpt-realtime-mini",
        extra_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:

        # Configurar sesión
        await openai_ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "instructions": (
                    "Eres un asistente telefónico en español. "+"Respondes de forma clara, breve y amable."
                ),
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16"
            }
        }))

        async def meta_to_openai():
            while True:
                data = await ws.receive_bytes()
                await openai_ws.send(json.dumps({
                    "type": "input_audio_buffer.appWSend",
                    "audio": data.hex()
                }))

        async def openai_to_meta():
            while True:
                msg = await openai_ws.recv()
                event = json.loads(msg)

                if event["type"] == "output_audio_buffer.append":
                    audio = bytes.fromhex(event["audio"])
                    await ws.send_bytes(audio)

        await asyncio.gather(
            meta_to_openai(),
            openai_to_meta()
        )
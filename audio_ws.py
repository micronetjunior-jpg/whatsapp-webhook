import asyncio
import json
import os
import websockets

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

REALTIME_URL = (
    "wss://api.openai.com/v1/realtime"
    "?model=gpt-realtime-mini"
)

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta": "realtime=v1"
}

async def realtime_agent():
    async with websockets.connect(
        REALTIME_URL,
        extra_headers=HEADERS
    ) as ws:

        # 1️⃣ Crear una sesión
        await ws.send(json.dumps({
            "type": "session.create",
            "session": {
                "modalities": ["text"],
                "instructions": (
                    "Eres un asistente experto en sistemas inteligentes "
                    "y agentes automatizados."
                )
            }
        }))

        # 2️⃣ Enviar un mensaje del usuario
        await ws.send(json.dumps({
            "type": "input_text_buffer.append",
            "text": "Explícame qué es un agente inteligente"
        }))

        await ws.send(json.dumps({
            "type": "input_text_buffer.commit"
        }))

        await ws.send(json.dumps({
            "type": "response.create"
        }))

        # 3️⃣ Escuchar respuestas
        while True:
            message = await ws.recv()
            event = json.loads(message)

            if event["type"] == "response.output_text.delta":
                print(event["delta"], end="", flush=True)

            if event["type"] == "response.completed":
                print("\n\n✔ Respuesta completada")
                break

asyncio.run(realtime_agent())
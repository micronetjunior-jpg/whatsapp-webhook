import asyncio
import websockets
import json
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

REALTIME_URL = (
    "wss://api.openai.com/v1/realtime?"
    "model=gpt-realtime-mini"
)

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta": "realtime=v1"
}

async def realtime_session():
    async with websockets.connect(
        REALTIME_URL,
        extra_headers=HEADERS
    ) as ws:

        # 1️⃣ Mensaje inicial del sistema
        await ws.send(json.dumps({
            "type": "response.create",
            "response": {
                "modalities": ["audio", "text"],
                "instructions": "Saluda al usuario y pregúntale en qué puedes ayudarle."
            }
        }))

        print("🎙️ GPT hablando...")

        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            print("🔁 Realtime:", data)

if __name__ == "__main__":
    asyncio.run(realtime_session())
import asyncio
from fastapi import FastAPI, Request, Response
from config import VERIFY_TOKEN
from handlers import handle_message
from fastapi.responses import JSONResponse
from audio_ws import *
import websockets
#import asyncio

async def test():
    async with websockets.connect(
        "wss://webhook-server-ambientepruebayy.up.railway.app/audio"
    ) as ws:
        print()
        print()
        print()
        print("Conectado al WS")
        await asyncio.sleep(10)
        
asyncio.run(test())

app = FastAPI()

@app.get("/webhook")
async def verify(request: Request):
    p = request.query_params
    if p.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=p.get("hub.challenge"))
    return Response(status_code=403)

@app.post("/webhook")
async def meta_webhook(request: Request):
    payload = await request.json()
    print("📞 EVENTO META:", payload)

    # Detectar evento de llamada
    if payload.get("event") == "call":
        return JSONResponse({
            "action": "connect",
            "stream": {
                # WebSocket donde Meta enviará el audio
                "url":"wss://webhook-server-ambienteprueba.up.railway.app/audio"
            }
        })
        print("llamada")
        return JSONResponse({"status": "ok"})
    else:
        data = await request.json()
        asyncio.create_task(handle_message(data))
        return Response(status_code=200)

    


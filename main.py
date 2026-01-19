import asyncio
from fastapi import FastAPI, Request, Response
from config import VERIFY_TOKEN
from handlers import handle_message
from fastapi.responses import JSONResponse
from audio_ws import *

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
                "url": "wss://webhook-server-ambienteprueba.up.railway.app/audio
            }
        })
        print("llamada")
        return JSONResponse({"status": "ok"})
    else:
        data = await request.json()
        asyncio.create_task(handle_message(data))
        return Response(status_code=200)

    


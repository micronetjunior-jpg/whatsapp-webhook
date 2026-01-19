from fastapi import FastAPI, Request, Response
from config import VERIFY_TOKEN
from handlers import handle_message
from fastapi.responses import JSONResponse
from audio_ws import *
import websockets
import asyncio

app = FastAPI()

# Webhook Meta
@app.post("/webhook")
async def meta_webhook(request: Request):
    payload = await request.json()
    print("📞 EVENTO META:", payload)

    if payload.get("event") == "call":
        return JSONResponse({
            "action": "connect",
            "stream": {
                "url": "wss://webhook-server-ambientepruebayy.up.railway.app/audio"
            }
        })

    return JSONResponse({"status": "ok"})


# WebSocket de audio
@app.websocket("/audio")
async def audio_ws(ws: WebSocket):
    await audio_endpoint(ws)
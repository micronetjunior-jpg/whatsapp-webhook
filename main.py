from fastapi import FastAPI, Request, Response
from config import VERIFY_TOKEN
from handlers import handle_message
from fastapi.responses import JSONResponse
#from audio_ws import *
import websockets
import asyncio

app = FastAPI()

@app.get("/webhook")
async def verify(request: Request):
    p = request.query_params
    if p.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=p.get("hub.challenge"))
    return Response(status_code=403)
    
    
async def test():
    async with websockets.connect(
        "wss://webhook-server-ambientepruebayy.up.railway.app/audio"
    ) as ws:
        print("Conectado al WS")
        await asyncio.sleep(10)

asyncio.run(test())
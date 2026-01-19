from fastapi import FastAPI, Request
import asyncio
import json
import os
import websockets
from config import *

app = FastAPI()

async def audio_endpoint(ws: WebSocket):
    await ws.accept()
    print("🔗 WebSocket /audio conectado")
    async with websockets.connect(
        "wss://api.openai.com/v1/realtime?model=gpt-realtime-mini",
        extra_headers={"Authorization": f"Bearer {OPENAI_API_KEY}","OpenAI-Beta": "realtime=v1"}) 
        
    
"""
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    try:
        #user_text = data.get("text", "Hola")
        reply = await call_realtime(user_text)
    return {"reply": reply}



{
  "prompt": {
    "id": "pmpt_696e7b7e25a88194910e42e88b46796f09b017994935008f",
    "version": "1"
  }
}

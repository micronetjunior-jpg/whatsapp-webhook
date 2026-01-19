from fastapi import FastAPI, Request
import asyncio
import json
import os
import websockets
from config import *

app = FastAPI()

MODEL = "gpt-realtime-mini"
REALTIME_URL = f"wss://api.openai.com/v1/realtime?model={MODEL}"

async def call_realtime(prompt: str) -> str:
    response_text = ""
    async with websockets.connect(
        REALTIME_URL,
        extra_headers=HEADERS)
    as ws:
        await ws.send(json.dumps({
            "type": "session.create",
            "session": {
            "modalities": ["text"],
            "instructions": "Eres un asistente experto en agentes inteligentes."} }))
        await ws.send(json.dumps({
            "type": "input_text_buffer.append",
            "text": prompt }))
        await ws.send(json.dumps({
            "type": "input_text_buffer.commit"}))
        await ws.send(json.dumps({
            "type": "response.create" }))

    while True:
        event = json.loads(await ws.recv())
        if event["type"] == "response.output_text.delta":
            response_text += event["delta"]
        if event["type"] == "response.completed":
            break
        return response_text
    
@app.post("/webhook")
    async def webhook(request: Request):
        data = await request.json()
        user_text = data.get("text", "Hola")
        reply = await call_realtime(user_text)
    return {"reply": reply}
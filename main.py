from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import os

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "verify_token_default")

@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return PlainTextResponse(params.get("hub.challenge"))
    return PlainTextResponse("Invalid verification token", status_code=403)

@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    print("📩 Mensaje recibido:", body)
    return {"status": "ok"}

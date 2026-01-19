from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE = "https://api.openai.com/v1/realtime/calls"

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

@app.post("/webhook/hangup/{call_id}")
def hangup(call_id: str):
    requests.post(
        f"{OPENAI_BASE}/{call_id}/hangup",
        headers=HEADERS
    )
    return {"status": "call terminated"}

"""
@app.post("/webhook/call")
async def incoming_call(request: Request):
    payload = await request.json()
    print("📞 CALL EVENT:", payload)
"""

    call_id = payload.get("call_id")

    if not call_id:
        return {"error": "No call_id received"}

    # 1️⃣ Aceptar la llamada
    accept = requests.post(
        f"{OPENAI_BASE}/{call_id}/accept",
        headers=HEADERS,
        json={
            "type": "realtime",
            "model": "gpt-realtime-mini",
            "voice": "alloy",
            "instructions": "Hola, gracias por llamar. Soy tu asistente virtual. ¿En qué puedo ayudarte?"
        }
    )

    print("✅ Call accepted:", accept.status_code)

    return {"status": "accepted", "call_id": call_id}
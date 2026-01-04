from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import os, httpx

app = FastAPI()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mi_token")
WPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_NUMBER_ID")

@app.get("/webhook")
async def verify(request: Request):
    q = request.query_params
    if q.get("hub.mode") == "subscribe" and q.get("hub.verify_token") == VERIFY_TOKEN:
        return PlainTextResponse(q.get("hub.challenge", ""))
    return PlainTextResponse("forbidden", status_code=403)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    try:
        value = data["entry"][0]["changes"][0]["value"]
        msg = value["messages"][0]
        to = msg["from"]
        text = msg.get("text", {}).get("body", "")

        url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
        headers = {"Authorization": f"Bearer {WPP_TOKEN}", "Content-Type": "application/json"}
        payload = {"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":"OK"}}

        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.post(url, headers=headers, json=payload)
            print("SEND:", r.status_code, r.text, "IN:", text)

    except Exception as e:
        print("ERR:", e)

    return {"ok": True}

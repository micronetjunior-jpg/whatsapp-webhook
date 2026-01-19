from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import ast
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)

VERIFY_TOKEN = "academia_verify_token"


# 1️⃣ Verificación de Meta (OBLIGATORIO)
@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None,
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logging.info("✅ Webhook verificado correctamente")
        return PlainTextResponse(hub_challenge)
    logging.warning("❌ Verificación fallida")
    return PlainTextResponse("Error", status_code=403)


# 2️⃣ Recepción de eventos (calls)
@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    logging.info(f"📩 Payload recibido: {payload}")

    # Meta a veces manda logs con message como string
    if "message" in payload:
        try:
            entries = ast.literal_eval(payload["message"])
            entry = entries[0]

            value = entry["changes"][0]["value"]

            if "calls" in value:
                call = value["calls"][0]

                logging.info("📞 LLAMADA DETECTADA")
                logging.info(f"Call ID: {call['id']}")
                logging.info(f"From: {call['from']}")
                logging.info(f"Status: {call['status']}")
                logging.info(f"Event: {call['event']}")

                # 👉 AQUÍ luego entra OpenAI Realtime
                start_realtime_session(call["id"])

        except Exception as e:
            logging.error(f"Error procesando message: {e}")

    return {"status": "ok"}
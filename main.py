import asyncio
from fastapi import FastAPI, Request, Response
from config import VERIFY_TOKEN
from handlers import handle_message
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/webhook")
async def verify(request: Request):
    p = request.query_params
    if p.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=p.get("hub.challenge"))
    return Response(status_code=403)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    asyncio.create_task(handle_message(data))
    return Response(status_code=200)






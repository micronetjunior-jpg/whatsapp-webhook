from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("\n\n📦 MENSAJE RECIBIDO:")
    print(data)
    return {"ok": True}

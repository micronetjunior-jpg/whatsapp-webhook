import json
import redis
from config import REDIS_URL

r = redis.from_url(REDIS_URL, decode_responses=True)

# -------- EVENTOS (media_id) --------

def get_event(event_id):
    data = r.get(f"event:{event_id}")
    return json.loads(data) if data else None

def set_event(event_id, status, ttl=300):
    r.setex(f"event:{event_id}", ttl, json.dumps({"status": status}))

# -------- LOCK POR USUARIO --------

def acquire_user_lock(telefono, ttl=120):
    return r.set(f"lock:user:{telefono}", "1", nx=True, ex=ttl)

def release_user_lock(telefono):
    r.delete(f"lock:user:{telefono}")

# -------- ESTADO CONVERSACIONAL --------

def guardar_estado(telefono, estado, data=None, ttl=300):
    r.setex(
        f"user:{telefono}",
        ttl,
        json.dumps({"estado": estado, "data": data})
    )

def obtener_estado(telefono):
    data = r.get(f"user:{telefono}")
    return json.loads(data) if data else None

# -------- HISTORIAL --------

def guardar_historial(telefono, mensajes):
    r.setex(f"chat:{telefono}", 3600, json.dumps(mensajes))

def obtener_historial(telefono):
    data = r.get(f"chat:{telefono}")
    return json.loads(data) if data else []
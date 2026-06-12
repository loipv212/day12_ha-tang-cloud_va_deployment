import time
import json
import uuid
import signal
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Header
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import redis

from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit
from .cost_guard import check_budget, record_cost
from .mock_llm import ask

logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

START_TIME = time.time()
_is_ready = False
_in_flight_requests = 0

def handle_sigterm(signum, frame):
    logger.info("Received SIGTERM, beginning graceful shutdown...")

signal.signal(signal.SIGTERM, handle_sigterm)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info("Starting up...")
    try:
        r.ping()
        _is_ready = True
        logger.info("Agent is ready!")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
    
    yield
    
    _is_ready = False
    logger.info("Shutting down... waiting for in-flight requests.")
    timeout = 30
    elapsed = 0
    while _in_flight_requests > 0 and elapsed < timeout:
        time.sleep(1)
        elapsed += 1
    logger.info("Shutdown complete.")

app = FastAPI(title="Production Ready AI Agent", lifespan=lifespan)

@app.middleware("http")
async def track_requests(request, call_next):
    global _in_flight_requests
    _in_flight_requests += 1
    try:
        return await call_next(request)
    finally:
        _in_flight_requests -= 1

class AskRequest(BaseModel):
    question: str
    user_id: str
    session_id: str | None = None

@app.get("/health")
def health():
    return {"status": "ok", "uptime_seconds": round(time.time() - START_TIME, 1)}

@app.get("/ready")
def ready():
    if not _is_ready:
        return JSONResponse(status_code=503, content={"status": "not ready"})
    try:
        r.ping()
        return {"status": "ready"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "redis down"})

@app.post("/ask")
def ask_endpoint(
    body: AskRequest,
    _auth: bool = Depends(verify_api_key)
):
    check_rate_limit(body.user_id)
    check_budget(body.user_id)
    
    session_id = body.session_id or str(uuid.uuid4())
    session_key = f"session:{session_id}"
    
    # Lấy history từ Redis
    history_data = r.get(session_key)
    history = json.loads(history_data) if history_data else []
    
    history.append({"role": "user", "content": body.question, "time": datetime.now(timezone.utc).isoformat()})
    
    answer = ask(body.question)
    
    history.append({"role": "assistant", "content": answer, "time": datetime.now(timezone.utc).isoformat()})
    
    r.setex(session_key, 3600, json.dumps(history))
    
    record_cost(body.user_id)
    
    return {
        "session_id": session_id,
        "answer": answer,
        "history_count": len(history)
    }

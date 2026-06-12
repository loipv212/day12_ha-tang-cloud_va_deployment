import redis
from datetime import datetime
from fastapi import HTTPException
from .config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

COST_PER_REQUEST = 0.05

def check_budget(user_id: str):
    """Kiểm tra budget hàng tháng."""
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current = float(r.get(key) or 0)
    if current + COST_PER_REQUEST > settings.MONTHLY_BUDGET_USD:
        raise HTTPException(status_code=402, detail="Monthly budget exceeded.")
        
def record_cost(user_id: str):
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    r.incrbyfloat(key, COST_PER_REQUEST)
    r.expire(key, 32 * 24 * 3600)

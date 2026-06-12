import time
import redis
from fastapi import HTTPException
from .config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_rate_limit(user_id: str):
    """Giới hạn request dùng sliding window qua Redis."""
    key = f"rate_limit:{user_id}"
    now = time.time()
    window = 60 # 1 phút
    
    # Xóa các request ngoài cửa sổ 60s
    r.zremrangebyscore(key, 0, now - window)
    
    # Đếm số request hiện tại
    requests = r.zcard(key)
    
    if requests >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    
    # Thêm request mới
    r.zadd(key, {str(now): now})
    r.expire(key, window)

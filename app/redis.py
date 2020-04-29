import redis

from app.settings import REDIS_URL

redis_client = redis.Redis(host=REDIS_URL, port=6379)

__all__ = ["redis_client"]

# lru_cache to cache the redis client
from functools import lru_cache
from redis import Redis
from backend.app.settings import get_settings

# create a redis client
@lru_cache
def get_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url,decode_responses=True)
    # decode_responses=True is used to decode the responses from the redis server
    # redis server returns bytes by default, so we need to decode it to a string
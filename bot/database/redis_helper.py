from aioredis import Redis

class RedisHelper:
    def __init__(self):
        self.redis = Redis()

redis_helper = RedisHelper()

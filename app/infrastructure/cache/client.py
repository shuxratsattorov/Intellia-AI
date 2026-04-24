import redis.asyncio as redis

# from app.core.config import settings


class RedisClient:
    def __init__(self):
        self._client = None

    async def connect(self):
        self._client = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
            # host=settings.REDIS_HOST,
            # port=settings.REDIS_PORT,
            # db=settings.REDIS_DB,
            # password=settings.REDIS_PASSWORD,
            # decode_responses=settings.DECODE_RESPONSES,
        )

    async def client(self) -> redis.Redis:
        if not self._client:
            try:
                await self.connect()
            except Exception:
                raise RuntimeError("Redis not initialized")
        return self._client

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None        


redis_client = RedisClient()
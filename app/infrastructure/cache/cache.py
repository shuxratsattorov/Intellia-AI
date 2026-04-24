import asyncio

from app.infrastructure.cache.client import RedisClient
from app.infrastructure.cache.keys import RedisKeys


class RedisCache:
    def __init__(self, redis_client, redis_keys):
        self.redis_client = redis_client
        self.redis_keys = redis_keys
    
    # --- OTP ----------------------------------------------------------------

    async def set_otp(self, flow: str, user_id: int, otp: str, ttl=300) -> bool:
        client = await self.redis_client.client()
        key = self.redis_keys.otp(flow, user_id)

        return await client.set(key, otp, ex=ttl)

    async def get_otp(self, flow: str, user_id: int) -> str | None:
        client = await self.redis_client.client()
        key = self.redis_keys.otp(flow, user_id)
        
        return await client.get(key)

    # # --- Attempts -----------------------------------------------------------

    async def increment_attempts(self, flow: str, user_id, ttl=300) -> str | None:
        client = await self.redis_client.client()
        key = self.redis_keys.attempts_otp(flow, user_id)
        count = await client.incr(key)

        if count == 1:
            await client.expire(key, ttl)

        return count

    # # --- Resend -------------------------------------------------------------
    
    async def increment_resend(self, flow: str, user_id: int, ttl=300) -> str | None:
        client = await self.redis_client.client()
        key = self.redis_keys.resend_otp(flow, user_id)
        count = await client.incr(key)

        if count == 1:
            await client.expire(key, ttl)

        return count

    # --- Cooldown -----------------------------------------------------------
 
    async def set_cooldown(self, flow: str, user_id: int, ttl=300) -> bool:
        client = await self.redis_client.client()
        key = self.redis_keys.cooldown_otp(flow, user_id)

        return await client.set(key, 1, ttl)
 
    # # --- Block --------------------------------------------------------------

    async def block_user(self, flow: str, user_id, ttl=600) -> bool:
        client = await self.redis_client.client()
        key = self.redis_keys.block_otp(flow, user_id)

        return await client.set(key, True, ttl)

    async def is_blocked(self, flow: str, user_id) -> str | None:
        client = await self.redis_client.client()
        key = self.redis_keys.block_otp(flow, user_id)

        return await client.get(key) is not None

    # --- Clean --------------------------------------------------------------

    async def cleanup_after_login(self, flow: str, user_id: int):
        client = await self.redis_client.client()


        keys = [
            self.redis_keys.otp(flow, user_id),
            self.redis_keys.attempts_otp(flow, user_id),
            self.redis_keys.resend_otp(flow, user_id),
            self.redis_keys.cooldown_otp(flow, user_id),
            self.redis_keys.block_otp(flow, user_id),
            self.redis_keys.attempts_login(user_id),
            self.redis_keys.block_login(user_id),
        ]

        await client.delete(*keys)


async def main():
    cache = RedisCache(RedisClient(), RedisKeys())

    print(await cache.set_otp("login", 1, "123456"))
    print(await cache.get_otp("login", 1))

    print(await cache.increment_attempts("login", 1))
    print(await cache.increment_resend("login", 1))


    print(await cache.set_cooldown("login", 1))
    # await cache.cleanup_after_login("login", 1)

asyncio.run(main())
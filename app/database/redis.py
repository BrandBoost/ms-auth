from typing import Any, Optional

import aioredis  # type: ignore

from app.config import settings


class RedisManager:
    redis_uri = settings.REDIS_URI
    # TODO check type for redis
    redis: Optional[Any] = None

    @classmethod
    async def connect(cls):
        cls.redis = await aioredis.create_redis_pool(cls.redis_uri)
        return cls

    @classmethod
    async def close(cls):
        cls.redis.close()
        await cls.redis.wait_closed()

    @classmethod
    def get_redis(cls):
        return cls.redis


class RedisRepository(RedisManager):
    async def set(self, key: str, value: Any, expire: Optional[int] = None):
        await self.redis.set(key, value, expire=expire)  # type: ignore

    async def get(self, key: str) -> Any:
        value = await self.redis.get(key)  # type: ignore
        return value

    async def delete(self, key: str):
        await self.redis.delete(key)  # type: ignore

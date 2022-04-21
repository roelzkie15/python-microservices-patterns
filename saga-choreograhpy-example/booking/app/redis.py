import aioredis
from app.dependencies import get_settings

settings = get_settings()
redis = aioredis.from_url(f'redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0')

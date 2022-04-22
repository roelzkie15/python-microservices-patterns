from functools import lru_cache

from app.settings import Settings

@lru_cache()
def get_settings():
    return Settings()

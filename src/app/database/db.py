import asyncpg
from collections.abc import AsyncGenerator
from app.secrets.infisical import SUPABASE_URL
from typing import Optional

db_url: str = SUPABASE_URL.secretValue

class AsyncManager(object):
    def __init__(self, db_url):
        self.db_url = db_url
        self.pool: Optional[asyncpg.Pool] = None

    async def async_connect(self):
        try:
            self.pool = await asyncpg.create_pool(dsn=self.db_url)
        except Exception as e:
            raise

    async def async_disconnect(self):
        try:
            if self.pool:
                await self.pool.close()
        except Exception as e:
            raise

async_manager = AsyncManager(db_url=db_url)

async def get_db() -> AsyncGenerator:
    try:
        async with async_manager.pool.acquire() as connection:
            yield connection
    except Exception as e:
        raise
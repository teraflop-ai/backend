import asyncpg
from app.secrets.infisical import SUPABASE_URL

db_url: str = SUPABASE_URL.secretValue

async def create_asyncpg_client():
    """
    Initialize asyncpg connection pool.
    """
    
    pool = await asyncpg.create_pool(dsn=db_url)
    try:
        yield pool
    finally:
        if pool:
            await pool.close()
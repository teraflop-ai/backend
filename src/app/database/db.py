import asyncpg
from collections.abc import AsyncGenerator
from app.secrets.infisical import SUPABASE_URL

db_url: str = SUPABASE_URL.secretValue

async def create_asyncpg_client() -> AsyncGenerator:
    """
    Initialize asyncpg connection pool.
    """
    
    pool = await asyncpg.create_pool(dsn=db_url)
    try:
        yield pool
    finally:
        if pool:
            await pool.close()


async def increment_balance(amount, user_id, asyncpg_client):
    async with asyncpg_client.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                """
                UPDATE users
                SET balance = balance + $1
                WHERE id = $2
                """, 
                amount, 
                user_id
            )


async def decrement_balance(amount, user_id, asyncpg_client):
    async with asyncpg_client.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                """
                UPDATE users
                SET balance = balance - $1
                WHERE id = $2
                """, 
                amount, 
                user_id
            )
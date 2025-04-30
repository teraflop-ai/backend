from app.schemas.users import User
from fastapi import Request, HTTPException
from app.dependencies.db import Client
import logfire
from loguru import logger


async def get_current_user(request: Request, asyncpg_client: Client) -> User:
    """
    """
    user_id = request.session.get('user_id')
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    try:
        
        async with asyncpg_client.acquire() as connection:
            user_record = await connection.fetchrow(
                """
                SELECT id, email, balance, google_id
                FROM users
                WHERE id = $1
                """,
                user_id
            )

        if not user_record:
            raise HTTPException(status_code=401, detail="User not found")

        user_data = dict(user_record)
        return User(**user_data)

    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve user data.")
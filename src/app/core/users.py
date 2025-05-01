from app.schemas.users import User
from fastapi import Request, HTTPException
from app.dependencies.db import AsyncDB
import logfire
from loguru import logger

API_KEY_NAME = "X-API-Key"
api_key_header_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_or_create_user():
    pass


async def get_user_by_id():
    pass


async def get_current_user(request: Request, db: AsyncDB) -> User:
    """
    """
    user_id = request.session.get('user_id')
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    try:
        user_record = await db.fetchrow(
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


async def get_user_by_api_key(api_key: str, db: AsyncDB):
    user_id = await db.fetchval(
        """
        """,
        api_key
    )
    return user_id


async def get_current_user_from_apikey():
    pass
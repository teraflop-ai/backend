from app.schemas.users import User
from fastapi import Request, HTTPException
from app.dependencies.db import Client
from loguru import logger


async def get_current_user(request: Request, Client):
    """
    """
    user_id = request.session.get('user_id')
    
    if not user_id:
         raise HTTPException(status_code=401, detail="User not authenticated")
    
    try:
        query = """
        SELECT id, email, balance, google_id
        FROM users
        WHERE id = user_id
        LIMIT 1
        """

        if not response.data:
            raise HTTPException(status_code=401, detail="User not found")

        user_data = response.data[0]
        return User(**user_data)

    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve user data.")
from app.schemas.users import User
from fastapi import Request, HTTPException, status
from app.dependencies.db import AsyncDB
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security.api_key import APIKeyHeader
from loguru import logger
from secrets import token_urlsafe
from app.schemas.users import User, UserAPIKey
from app.infisical.infisical import SESSION_SECRET_KEY
from pwdlib import PasswordHash

SECRET_KEY = SESSION_SECRET_KEY.secretValue
ALGORITHM = "HS256"
API_KEY_NAME = "X-API-Key"
api_key_header_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_user(user: dict, db: AsyncDB):
    """
    """
    try:
        user_record = await db.fetchrow(
            """
            INSERT INTO users (email, full_name, google_id, picture_url)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """,
            user.get("email"),
            user.get("name"),
            user.get("sub"),
            user.get("picture"),
        )
        if user_record:
            logger.info(f"Created user: {user_record}")
            return User(**dict(user_record))
        else:
            logger.error("Failed to create user")
            raise Exception("User creation failed")
    except Exception as e:
        logger.error({e})
        raise


async def get_user_by_email(email: str, db: AsyncDB):
    """
    """
    try:
        user_by_email = await db.fetchrow(
            """
            SELECT *
            FROM users
            WHERE email = $1
            LIMIT 1
            """,
            email,
        )
        if user_by_email:
            logger.info(f"{user_by_email}")
            return User(**dict(user_by_email))
        else:
            logger.error("Failed to get user email")
            return None
    except Exception as e:
        logger.error(f"{e}")
        raise


async def get_user_by_google_id(google_id, db: AsyncDB):
    """
    """
    try:
        user_by_google_id = await db.fetchrow(
            """
            SELECT *
            FROM users
            WHERE google_id = $1
            """,
            google_id,
        )
        if user_by_google_id:
            logger.info()
            return User(**dict(user_by_google_id))
        else:
            logger.error()
            raise Exception()
    except Exception as e:
        logger.error()
        raise


async def get_user_by_id(user_id, db: AsyncDB):
    """
    """
    try:
        user_by_id = await db.fetchrow(
            """
            SELECT *
            FROM users
            WHERE id = $1
            """,
            user_id,
        )
        if user_by_id:
            logger.info()
            return User(**dict(user_by_id))
        else:
            logger.error("Failed to get user")
            raise Exception()
    except Exception as e:
        logger.error()
        raise


async def get_user_by_api_key(api_key: str, db: AsyncDB):
    """
    """
    try:
        user_by_api_key = await db.fetchrow(
            """
            SELECT *
            FROM users
            WHERE user_api_key = $1
            """,
            api_key,
        )
        if user_by_api_key:
            return User(**dict(user_by_api_key))
        else:
            logger.info()
            raise Exception()
    except Exception as e:
        logger.info()
        raise


async def get_current_user(request: Request, db: AsyncDB) -> User:
    """
    """
    token = request.cookies.get("access_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        logger.error(f"{credentials_exception}")
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            logger.error(f"{user_email}")
            raise HTTPException(status_code=401, detail="User not authenticated")
    except JWTError:
        logger.error("Reeeee")
        raise credentials_exception

    try:
        user_record = await get_user_by_email(user_email, db)
        if not user_record:
            logger.error(f"Found user by email: {user_record}")
            raise credentials_exception
        return user_record
    except Exception as e:
        logger.error(f"Error fetching user {user_record}: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve user data.")


async def delete_current_user(
    user_id,
    db: AsyncDB,
):
    """
    """
    try:
        deleted_user = await db.fetchrow(
            """
            DELETE FROM users
            WHERE user_id
            RETURNING *
            """,
            user_id,
        )
        if deleted_user:
            logger.info(f"Successfully deleted user: {deleted_user}")
            return
        else:
            logger.error("Failed to delete user")
            raise
    except Exception as e:
        logger.error("Reeeeeee")
        raise
        

def generate_api_key():
    api_key = "tf_" + token_urlsafe(32)
    return api_key


async def create_user_api_key(user, db: AsyncDB):
    """
    """

    # need to encrypt api key before storage

    random_api_key = generate_api_key()
    try:
        user_api_key = await db.fetchrow(
            """
            INSERT INTO user_api_keys (api_key)
            VALUE = ($1)
            RETURNING *
            """,
            random_api_key
        )
        if user_api_key:
            logger.info()
            return
        else:
            logger.error()
            raise
    except Exception as e:
        logger.error()
        raise


async def delete_user_api_key(user_id: int, db: AsyncDB):
    try:
        user_api_key = await db.fetchrow(
            """
            
            FROM user_api_keys
            WHERE 
            """,
            user_id,
        )
    except:
        raise


# async def user_from_api_key(
#     apikey,
#     db: AsyncDB
# ):
#     try:
#         current_user = db.fetchrow(
#             """

#             """,
#             apikey,
#         )
#     except:
#         raise

async def list_user_api_keys(user_id: int, db: AsyncDB):
    try:
        user_api_keys = db.fetch(
            """
            SELECT *
            FROM user_api_keys
            WHERE user_id = $1 AND is_active = TRUE
            """,
            user_id,
        )
        if user_api_keys:
            logger.info(f"Found user api keys: {user_api_keys}")
            return [UserAPIKey(**dict(key)) for key in user_api_keys]
    except:
        raise
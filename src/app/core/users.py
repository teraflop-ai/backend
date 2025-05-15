from app.schemas.users import User
from fastapi import Request, HTTPException, status
from app.dependencies.db import AsyncDB
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security.api_key import APIKeyHeader
from loguru import logger
from secrets import token_urlsafe
from app.schemas.users import User

SECRET_KEY = 1
ALGORITHM = 1
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
    try:
        user_record = await db.execute(
            """
            INSERT INTO users (email, name, google_id, picture_url)
            VALUES ($1, $2, $3, $4)
            """,
            user.get("email"),
            user.get("name"),
            user.get("sub"),
            user.get("picture"),
        )
        if not user_record:
            logger.error("Failed to create user")
            raise Exception("User creation failed")
        return User(**dict(user_record))
    except Exception as e:
        logger.error()
        raise


async def get_user_by_email(email: str, db: AsyncDB):
    try:
        user_by_email = await db.fetchrow(
            """
            SELECT *
            FROM users
            WHERE email = $1
            """,
            email,
        )
        if not user_by_email:
            logger.error("Failed to get user email")
            raise Exception()
        return User(**dict(user_by_email))
    except Exception as e:
        logger.error()
        raise


async def get_user_by_google_id(google_id, db: AsyncDB):
    try:
        user_by_google_id = await db.fetchrow(
            """
            SELECT *
            FROM users
            WHERE google_id = $1
            """,
            google_id,
        )
        if not user_by_google_id:
            logger.error()
            raise Exception()
        return user_by_google_id
    except Exception as e:
        logger.error()
        raise


async def get_user_by_id(user_id, db: AsyncDB):
    try:
        user_by_id = await db.fetchrow(
            """
            SELECT *
            FROM users
            WHERE id = $1
            """,
            user_id,
        )
        if not user_by_id:
            logger.error("Failed to get user")
            raise Exception()
        return User(**dict(user_by_id))
    except Exception as e:
        logger.error()
        raise


async def get_current_user(request: Request) -> User:
    token = request.cookies.get("access_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            logger.error()
            raise HTTPException(status_code=401, detail="User not authenticated")
    except JWTError:
        logger.error()
        raise credentials_exception

    try:
        user_record = get_user_by_email(user_email)
        if not user_record:
            logger.error()
            raise credentials_exception
        return User(dict(**user_record))
    except Exception as e:
        logger.error(f"Error fetching user {user_record}: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve user data.")


def generate_api_key():
    api_key = token_urlsafe(32)
    return api_key


async def create_user_api_key(user, db: AsyncDB):
    random_api_key = generate_api_key()
    try:
        await db.execute(
            """
            INSERT INTO user_api_keys (api_key)
            VALUE = ($1)
            """,
            random_api_key
        )
    except Exception as e:
        logger.error()
        raise


async def delete_user_api_key(db: AsyncDB):
    try:
        await db.execute()
    except:
        pass


async def get_user_by_api_key(api_key: str, db: AsyncDB):
    try:
        user_id = await db.fetchrow(
            """
            SELECT *
            FROM users
            WHERE user_api_key = $1
            """,
            api_key,
        )
        return user_id
    except Exception as e:
        raise


async def get_current_user_from_apikey():
    pass


async def user_me():
    pass

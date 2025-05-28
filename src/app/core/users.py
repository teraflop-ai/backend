from fastapi import Request, HTTPException, status
from app.dependencies.db import AsyncDB
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger
from secrets import token_urlsafe
from app.schemas.users import (
    User, UserAPIKey, UserDeleteAPIKey
)
from app.infisical.infisical import SESSION_SECRET_KEY
import hashlib
from pwdlib import PasswordHash

SECRET_KEY = SESSION_SECRET_KEY.secretValue
ALGORITHM = "HS256"
hasher = PasswordHash.recommended()

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
        async with db.transaction():
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
            if not user_record:
                raise

            logger.info(f"Created user: {user_record}")
            user_id = user_record['id']
            balance_record = await db.fetchrow(
                """
                INSERT INTO user_balance (user_id)
                VALUES ($1)
                RETURNING *
                """,
                user_id,
            )
            if not balance_record:
                raise
            logger.info(f"Created balance for user: {balance_record}")
            return User(**dict(user_record))

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


async def get_user_by_google_id(google_id: str, db: AsyncDB):
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


async def get_user_by_id(user_id: int, db: AsyncDB):
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
        logger.error("Failed to decode JWT")
        raise credentials_exception

    try:
        user_record = await get_user_by_email(user_email, db)
        logger.info(f"Found user record {user_record}")
        if not user_record:
            logger.error(f"User not found by email: {user_record}")
            raise credentials_exception
        return user_record
    except Exception as e:
        logger.error(f"Error fetching user email {user_email}: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve user data.")


async def delete_user(user_id: int, db: AsyncDB):
    """
    """
    try:
        deleted_user = await db.fetchrow(
            """
            DELETE FROM users
            WHERE id = $1
            RETURNING *
            """,
            user_id,
        )
        if deleted_user:
            logger.info(f"Successfully deleted user: {deleted_user}")
            return deleted_user
        else:
            logger.error("Failed to delete user")
            raise
    except Exception as e:
        logger.error("Reeeeeee")
        raise
        

async def set_last_logged_in(user, db: AsyncDB):
    try:
        await db.execute(
            """
            UPDATE users 
            SET last_logged_in_at = CURRENT_TIMESTAMP 
            WHERE id = $1
            """,
            user.id
        )
    except:
        raise


async def get_user_by_api_key(api_key: str, db: AsyncDB):
    """
    """
    try:
        lookup_hash = hashlib.sha256(api_key.encode()).hexdigest()
        user_by_api_key = await db.fetchrow(
            """
            SELECT *
            FROM user_api_keys
            WHERE lookup_hash = $1
            """,
            lookup_hash
        )
        if user_by_api_key:
            if verify_api_key(api_key, user_by_api_key["hashed_key"]):
                logger.info("User found from api key")
                return UserAPIKey(**dict(user_by_api_key))
            else:
                raise
        else:
            logger.info("FAILED TO GET USER FROM API KEY")
            raise
    except Exception as e:
        logger.info("EXCEPTION THROWN ON GET USER FUNCTION")
        raise


def generate_api_key():
    secret = token_urlsafe(32)
    prefix = "tf_"
    api_key = f"{prefix}{secret}"
    return api_key, prefix   


def create_api_key_hashes(api_key: str):
    lookup_hash = hashlib.sha256(api_key.encode()).hexdigest()
    verify_hash = hasher.hash(api_key)
    return lookup_hash, verify_hash


def verify_api_key(api_key: str, hash: str):
    return hasher.verify(api_key, hash)


async def create_user_api_key(api_key_name: str, user_id: int, db: AsyncDB):
    api_key, key_prefix = generate_api_key()
    lookup_hash, hashed_api_key = create_api_key_hashes(api_key)
    try:
        record = await db.fetchrow(
            """
            INSERT INTO user_api_keys (name, lookup_hash, hashed_key, user_id, key_prefix)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *;
            """,
            api_key_name,
            lookup_hash,
            hashed_api_key,
            user_id,
            key_prefix,
        )
        if record:
            logger.info(f"Created user: {record} api key: {api_key}")
            return {'api_key': api_key, 'record': UserAPIKey(**dict(record))}
        else:
            raise Exception("Failed to create user api key")
    except Exception as e:
        raise


async def delete_user_api_key(api_key_id: int, user_id: int, db: AsyncDB):
    try:
        user_api_key = await db.fetchrow(
            """
            DELETE FROM user_api_keys
            WHERE id = $1 AND user_id = $2
            RETURNING id
            """,
            int(api_key_id),
            user_id
        )
        return UserDeleteAPIKey(**dict(user_api_key))
    except:
        raise


async def list_user_api_keys(user_id: int, db: AsyncDB):
    try:
        user_api_keys = await db.fetch(
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
        else:
            logger.info("No api keys found")
            return None
    except:
        raise



async def get_user_token_usage(user_id: int, db: AsyncDB):
    pass

async def update_user_token_usage(user_int: int, db: AsyncDB):
    pass
from fastapi import Request, HTTPException, status
from app.dependencies.db import AsyncDB
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger
from secrets import token_urlsafe
from app.schemas.users import (
    User, 
    APIKey, 
    DeleteAPIKey
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
            return User(**dict(user_record))

    except Exception as e:
        logger.error({e})
        raise


async def get_user_by_email(email: str, db: AsyncDB):
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
    except:
        raise Exception("Failed to delete user")
        

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
                return APIKey(**dict(user_by_api_key))
            else:
                raise
        else:
            logger.info("FAILED TO GET USER FROM API KEY")
            raise
    except Exception as e:
        logger.info("EXCEPTION THROWN ON GET USER FUNCTION")
        raise


async def check_user_has_organization(user_id: int, db: AsyncDB):
    """
    Check if the user has an organization.
    For when authenticating first time sign up flow.
    """
    try:
        user_organization = await db.fetchrow(
            """
            SELECT organization_id
            FROM organization_members
            WHERE user_id = $1
            LIMIT 1;
            """,
            user_id
        )
        return user_organization
    except:
        raise Exception("Failed to check for user organizations")


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


async def create_api_key(
    api_key_name: str, 
    organization_id: int,
    project_id: int, 
    user_id: int, 
    db: AsyncDB
):
    api_key, key_prefix = generate_api_key()
    lookup_hash, hashed_api_key = create_api_key_hashes(api_key)
    try:
        record = await db.fetchrow(
            """
            INSERT INTO api_keys (
                name, 
                lookup_hash, 
                hashed_key, 
                user_id, 
                organization_id,
                project_id, 
                key_prefix
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *;
            """,
            api_key_name,
            lookup_hash,
            hashed_api_key,
            user_id,
            organization_id,
            project_id,
            key_prefix,
        )
        if record:
            logger.info(f"Created user: {record} api key: {api_key}")
            return {'api_key': api_key, 'record': APIKey(**dict(record))}
        else:
            raise Exception("Failed to create user api key")
    except:
        raise Exception("Failed to create API key")


async def delete_api_key(
    api_key_id: int,
    organization_id: int,
    user_id: int, 
    db: AsyncDB
):
    try:
        user_api_key = await db.fetchrow(
            """
            DELETE FROM api_keys
            WHERE id = $1 
            AND user_id = $2 
            AND organization_id = $3
            RETURNING id
            """,
            int(api_key_id),
            user_id,
            organization_id,
        )
        return DeleteAPIKey(**dict(user_api_key))
    except:
        raise Exception("Failed to delete API key")


# async def list_api_keys(organization_id: int, db: AsyncDB):
#     try:
#         api_keys = await db.fetch(
#             """
#             SELECT 
#                 ak.*,
#                 p.name as project_name
#             FROM api_keys ak
#             LEFT JOIN projects p ON ak.project_id = p.id
#             WHERE ak.organization_id = $1 AND ak.is_active = TRUE
#             ORDER BY ak.created_at DESC
#             """,
#             organization_id,
#         )
#         if api_keys:
#             logger.info(f"Found user api keys: {api_keys}")
#             return [APIKey(**dict(key)) for key in api_keys]
#         else:
#             logger.info("No api keys found")
#             return None
#     except:
#         raise Exception("Failed to get API keys")

    
async def list_project_api_keys(organization_id: int, project_id: int, db: AsyncDB):
    try:
        api_keys = await db.fetch(
            """
            SELECT *
            FROM api_keys
            WHERE organization_id = $1 
            AND project_id = $2 
            AND is_active = TRUE
            """,
            organization_id,
            project_id
        )
        if api_keys:
            logger.info(f"Found user api keys: {api_keys}")
            return [APIKey(**dict(key)) for key in api_keys]
        else:
            logger.info("No api keys found")
            return None
    except:
        raise Exception("Failed to get API keys")



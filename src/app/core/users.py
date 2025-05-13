from app.schemas.users import User
from fastapi import Request, HTTPException, status
from app.dependencies.db import AsyncDB
from jose import JWTError, jwt

API_KEY_NAME = "X-API-Key"
api_key_header_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def create_user(user, db: AsyncDB):
    try:
        await db.execute(
            """
            INSERT INTO users (email, google_id, name, picture_url)
            VALUES ($1, $2, $3, $4)
            """,
            user.get("email"),
            user.get("sub"),
            user.get("name"),
            user.get("picture")
        )
    except Exception as e:
        raise

async def get_user_by_email(email: str, db: AsyncDB):
    try:
        user_email = await db.fetchval(
            """
            SELECT email
            FROM users
            WHERE email = $1
            """,
            email,
        )
        return user_email
    except Exception as e:
        raise

async def get_user_by_google_id(google_id, db: AsyncDB):    
    try:
        user_google_id = await db.fetchval(
            """
            SELECT google_id
            FROM users
            WHERE google_id = $1
            """,
            google_id
        )
        return user_google_id
    except Exception as e:
        raise

async def get_user(user_id, db: AsyncDB):
    user_record = await db.fetchrow(
        """
        SELECT id, email, google_id
        FROM users
        WHERE id = $1
        """,
        user_id
    )
    return user_record

async def get_current_user(request: Request, db: AsyncDB) -> User:
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
        user_id = payload.get('user_id')

    except JWTError:
        raise credentials_exception

    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    try:

        user_record = get_user(user_id, db)
        if not user_record:
            raise HTTPException(status_code=401, detail="User not found")

        user_data = dict(user_record)
        return User(**user_data)

    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve user data.")


async def get_user_by_api_key(api_key: str, db: AsyncDB):
    try:
        user_id = await db.fetchval(
            """
            """,
            api_key
        )
        return user_id
    except Exception as e:
        raise

async def get_current_user_from_apikey():
    pass

async def user_me():
    pass 
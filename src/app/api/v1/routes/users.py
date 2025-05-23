from fastapi import Depends
from datetime import timedelta
from loguru import logger
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import (
    APIRouter,
    status, 
    Request, 
    HTTPException, 
    Response
)
from fastapi.responses import RedirectResponse
from starlette.config import Config
from app.schemas.users import UserAPIKey
from app.dependencies.db import AsyncDB
from app.core.users import (
    get_current_user,
    create_user_api_key,
    list_user_api_keys,
    get_user_by_api_key,
    delete_user,
    delete_user_api_key,
)
from starlette.status import HTTP_303_SEE_OTHER
import msgspec
from typing import List
from pydantic import BaseModel

user_router = APIRouter(
    prefix="/users", 
    tags=["Users"]
)


@user_router.get("/me")
async def user_me(current_user = Depends(get_current_user)):
    logger.info(current_user)
    return msgspec.to_builtins(current_user)


@user_router.delete("/delete")
async def delete_current_user(response: Response, db: AsyncDB, current_user=Depends(get_current_user)):
    await delete_user(current_user.id, db)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        # domain=".yourdomain.com"
    )
    logger.info("Successfully logged out")
    return {"message": "User deleted successfully"}


@user_router.get("/list-api-keys")
async def list_current_user_api_keys(
    db: AsyncDB,
    current_user = Depends(get_current_user)
):
    user_api_keys = await list_user_api_keys(current_user.id, db)
    return msgspec.to_builtins(user_api_keys)


@user_router.post("/create-api-key")
async def create_current_user_api_key(
    db: AsyncDB,
    current_user = Depends(get_current_user)
):
    created_api_key = await create_user_api_key(current_user.id, db)
    return msgspec.to_builtins(created_api_key)

class DeleteAPIKeyRequest(BaseModel):
    api_key_id: str

@user_router.delete("/delete-api-key")
async def delete_key(
    request: Request, 
    db: AsyncDB,
    current_user = Depends(get_current_user)
):
    body = await request.json()
    api_key_id = body.get("request_data")
    logger.info(f"User {current_user.id} deleting API key: {api_key_id}")
    result = await delete_user_api_key(api_key_id, current_user.id, db)
    return

# @user_router.get("/")
# async def get_current_user_by_api_key(
#     curren_user
# ):
#     return

async def update_user():
    pass

async def create_user():
    pass
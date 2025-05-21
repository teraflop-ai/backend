from fastapi import Depends
from datetime import timedelta
from loguru import logger
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from starlette.config import Config
from app.schemas.users import UserAPIKey
from app.dependencies.db import AsyncDB
from app.core.users import (
    get_current_user,
    create_user_api_key,
    list_user_api_keys,
    get_user_by_api_key,
)
import msgspec
from typing import List

user_router = APIRouter(
    prefix="/users", 
    tags=["Users"]
)


async def create_user():
    pass


@user_router.get("/me")
async def user_me(current_user = Depends(get_current_user)):
    return msgspec.to_builtins(current_user)


async def update_user():
    pass


async def delete_user():
    pass


@user_router.get("/list-api-keys", response_model=List[UserAPIKey])
async def list_current_user_api_keys(
    db: AsyncDB,
    current_user = Depends(get_current_user)
):
    list_user_api_keys = await list_user_api_keys(current_user.id, db)
    return msgspec.to_builtins(list_user_api_keys)


@user_router.post("/create-api-key")
async def create_current_user_api_key(
    db: AsyncDB,
    current_user = Depends(get_current_user)
):
    created_api_key = await create_user_api_key(current_user.id, db)
    return msgspec.to_builtins(created_api_key)


# @user_router.get("/")
# async def get_current_user_by_api_key(
#     curren_user
# ):
#     return
from loguru import logger
from fastapi import (
    APIRouter,
    Request, 
    Response,
)
from app.dependencies.users import CurrentUser
from app.dependencies.db import AsyncDB
from app.core.users import (
    create_api_key,
    list_api_keys,
    delete_user,
    delete_api_key,
    check_user_has_organization
)
from app.core.organizations import (
    check_if_member_exists,
    create_organization,
)
from app.core.projects import create_initial_project
from app.schemas.users import WelcomePayload
import msgspec
from typing import List


user_router = APIRouter(
    prefix="/users", 
    tags=["Users"]
)


@user_router.get("/me")
async def user_me(db: AsyncDB, current_user: CurrentUser):
    logger.info(current_user)
    user_id = current_user.id
    user_organization = await check_user_has_organization(user_id, db)
    onboarding_complete = user_organization is not None
    logger.info(onboarding_complete)
    return {
        "current_user": msgspec.to_builtins(current_user), 
        "onboarding_complete": onboarding_complete
    }


@user_router.post("/welcome/me")
async def user_onboarding(payload: WelcomePayload, db: AsyncDB, current_user: CurrentUser):
    logger.info(f"Welcome payload: {payload}")
    # check if the user exists
    member_exists = await check_if_member_exists(current_user.id, db)
    logger.info(member_exists)
    if member_exists:
        raise

    # if the member does not exist create the organization and project
    async with db.transaction():
        organization = await create_organization(
            current_user.id, 
            payload.organization, 
            db
        )
        logger.info(f"Organization info: {organization}")
        await create_initial_project(
            current_user.id, 
            payload.project,
            organization["id"], 
            db
        )
    return { "message" : "Onboarding successful" }


@user_router.delete("/delete")
async def delete_current_user(response: Response, db: AsyncDB, current_user: CurrentUser):
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
async def list_organization_api_keys(db: AsyncDB, current_user: CurrentUser):
    api_keys = await list_api_keys(current_user.last_selected_organization_id, db)
    return msgspec.to_builtins(api_keys)


@user_router.post("/create-api-key")
async def create_organization_api_key(request: Request, db: AsyncDB, current_user: CurrentUser):
    body = await request.json()
    api_key_name = body.get("name")
    logger.info(f"API key name {api_key_name}")
    created_api_key = await create_api_key(
        api_key_name, 
        current_user.last_selected_organization_id,
        current_user.last_selected_project_id, 
        current_user.id, 
        db
    )
    return msgspec.to_builtins(created_api_key)


@user_router.delete("/delete-api-key")
async def delete_organization_api_key(request: Request, db: AsyncDB, current_user: CurrentUser):
    body = await request.json()
    api_key_id = body.get("api_key_id")
    logger.info(f"User {current_user.id} deleting API key: {api_key_id}")
    deleted_api_key = await delete_api_key(
        api_key_id, 
        current_user.last_selected_organization_id,
        current_user.last_selected_project_id, 
        current_user.id, 
        db
    )
    return msgspec.to_builtins(deleted_api_key)


async def update_current_user():
    pass
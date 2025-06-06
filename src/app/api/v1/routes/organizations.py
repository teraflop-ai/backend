from loguru import logger
from fastapi import (
    APIRouter, 
    Request
)
from app.dependencies.users import CurrentUser
from app.dependencies.db import AsyncDB
from app.core.organizations import (
    get_organizations, 
    select_organization,
    list_organization_api_keys,
    create_organization_api_key,
    get_organization_members,
    update_organization_name
)
import msgspec


organization_router = APIRouter(
    prefix="/organizations", 
    tags=["Organizations"]
)


@organization_router.get("/get-organizations")
async def get_all_organizations(db: AsyncDB, current_user: CurrentUser):
    organizations = await get_organizations(
        current_user.last_selected_organization_id,
        db
    )
    return msgspec.to_builtins(organizations)


@organization_router.put("/select-organization")
async def select_current_organization(request: Request, current_user: CurrentUser, db: AsyncDB):
    body = await request.json()
    project_id = body.get("project_id")
    organization_id = body.get("organization_id")
    selected_organization = await select_organization(
        project_id,
        organization_id,
        current_user.id,
        db
    )
    return msgspec.to_builtins(selected_organization)


@organization_router.get("/list-api-keys")
async def list_all_organization_api_keys(db: AsyncDB, current_user: CurrentUser):
    api_keys = await list_organization_api_keys(current_user.last_selected_organization_id, db)
    return msgspec.to_builtins(api_keys)


@organization_router.post("/create-api-key")
async def create_organization_api_key_(request: Request, db: AsyncDB, current_user: CurrentUser):
    body = await request.json()
    api_key_name = body.get("name")
    project_id = body.get("project_id")
    logger.info(f"API key name {api_key_name}")
    created_api_key = await create_organization_api_key(
        api_key_name, 
        current_user.last_selected_organization_id,
        project_id, 
        current_user.id, 
        db
    )
    return msgspec.to_builtins(created_api_key)


@organization_router.get("/get-organization-members")
async def get_all_organization_members(db: AsyncDB, current_user: CurrentUser):
    organization_members = await get_organization_members(
        current_user.last_selected_organization_id,
        db
    )
    return msgspec.to_builtins(organization_members)


@organization_router.put("/update-organization-name")
async def update_current_organization_name(request: Request, db: AsyncDB, current_user: CurrentUser):
    body = await request.json()
    logger.info(body)
    organization_name = body.get("organization_name")
    organization_name = await update_organization_name(
        organization_name,
        current_user.last_selected_organization_id,
        db
    )
    return msgspec.to_builtins(organization_name)
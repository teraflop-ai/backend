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
    list_organization_api_keys
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
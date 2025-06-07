from loguru import logger
from fastapi import (
    APIRouter, 
    Request,
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
from msgspec import Struct
from pydantic import BaseModel

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

class SelectOrganization(BaseModel):
    project_id: int
    organization_id: int

@organization_router.put("/select-organization")
async def select_current_organization(
    payload: SelectOrganization, 
    current_user: CurrentUser, 
    db: AsyncDB
):
    selected_organization = await select_organization(
        payload.project_id,
        payload.organization_id,
        current_user.id,
        db
    )
    return msgspec.to_builtins(selected_organization)


@organization_router.get("/list-api-keys")
async def list_all_organization_api_keys(db: AsyncDB, current_user: CurrentUser):
    api_keys = await list_organization_api_keys(current_user.last_selected_organization_id, db)
    return msgspec.to_builtins(api_keys)

class CreateOrganizationAPIKey(BaseModel):
    name: str
    project_id: int

@organization_router.post("/create-api-key")
async def create_organization_api_key_(
    payload: CreateOrganizationAPIKey, 
    db: AsyncDB, 
    current_user: CurrentUser
):
    created_api_key = await create_organization_api_key(
        payload.name, 
        current_user.last_selected_organization_id,
        payload.project_id, 
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


class UpdateOrganizationName(BaseModel):
    organization_name: str

@organization_router.put("/update-organization-name")
async def update_current_organization_name(
    payload: UpdateOrganizationName, 
    db: AsyncDB, 
    current_user: CurrentUser
):
    organization_name = await update_organization_name(
        payload.organization_name,
        current_user.last_selected_organization_id,
        db
    )
    return msgspec.to_builtins(organization_name)
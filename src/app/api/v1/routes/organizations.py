from loguru import logger
from fastapi import (APIRouter,)
from app.dependencies.users import CurrentUser
from app.dependencies.db import AsyncDB
from app.core.organizations import get_organizations
import msgspec
from typing import List


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
async def select_organization():
    pass
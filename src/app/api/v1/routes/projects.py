from loguru import logger
from fastapi import (
    APIRouter, 
    Request
)
from app.dependencies.users import CurrentUser
from app.dependencies.db import AsyncDB
from app.core.projects import (
    create_new_project, 
    get_projects,
    select_project
)
import msgspec
from typing import List


project_router = APIRouter(
    prefix="/projects", 
    tags=["Projects"]
)


@project_router.get("/get-projects")
async def get_all_projects(db: AsyncDB, current_user: CurrentUser):
    projects = await get_projects(
        current_user.last_selected_organization_id,
        db
    )
    return msgspec.to_builtins(projects)


@project_router.post("/create-project")
async def create_project(request: Request, db: AsyncDB, current_user: CurrentUser):
    
    body = await request.json()
    project_name = body.get("name")
    
    new_project = await create_new_project(
        current_user.id,
        project_name,
        current_user.last_selected_organization_id,
        db
    )
    return new_project


@project_router.put("/select-project")
async def select_a_project(request: Request, current_user: CurrentUser, db: AsyncDB):
    body = await request.json()
    project_id = body.get("project_id")
    organization_id = body.get("organization_id")
    selected_project = await select_project(
        project_id,
        organization_id,
        current_user.id,
        db
    )
    return selected_project
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
    select_project,
    list_project_api_keys,
    create_project_api_key,
    get_project_members,
    get_current_project
)
import msgspec
from pydantic import BaseModel

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

class CreateProject(BaseModel):
    name: str

@project_router.post("/create-project")
async def create_project(
    payload: CreateProject, 
    db: AsyncDB, 
    current_user: CurrentUser
):
    new_project = await create_new_project(
        current_user.id,
        payload.name,
        current_user.last_selected_organization_id,
        db
    )
    return new_project

class SelectProject(BaseModel):
    project_id: int
    organization_id: int

@project_router.put("/select-project")
async def select_current_project(
    payload: SelectProject, 
    current_user: CurrentUser, 
    db: AsyncDB
):
    selected_project = await select_project(
        payload.project_id,
        payload.organization_id,
        current_user.id,
        db
    )
    return selected_project


@project_router.get("/list-api-keys")
async def list_all_project_api_keys(db: AsyncDB, current_user: CurrentUser):
    api_keys = await list_project_api_keys(
        current_user.last_selected_organization_id,
        current_user.last_selected_project_id, 
        db
    )
    return msgspec.to_builtins(api_keys)

class CreateProjectAPIKey(BaseModel):
    name: str
    project_id: int

@project_router.post("/create-api-key")
async def create_project_api_key_(
    payload: CreateProjectAPIKey, 
    db: AsyncDB, 
    current_user: CurrentUser
):
    created_api_key = await create_project_api_key(
        payload.name, 
        current_user.last_selected_organization_id,
        payload.project_id, 
        current_user.id, 
        db
    )
    return msgspec.to_builtins(created_api_key)


@project_router.get("/get-current-project")
async def get_project(db: AsyncDB, current_user: CurrentUser):
    current_project = await get_current_project(
        current_user.last_selected_project_id, 
        db
    )
    return msgspec.to_builtins(current_project)

class UpdateProjectName(BaseModel):
    name: str

@project_router.put("/update-project-name")
async def update_project_name(
    payload: UpdateProjectName, 
    db: AsyncDB, 
    current_user: CurrentUser
):
    try:
        await db.execute(
            """
            UPDATE projects
            SET name = $1, updated_at = NOW()
            WHERE id = $2
            """,
            payload.name,
            current_user.last_selected_project_id
        )
        return {"success": True}
    except:
        raise Exception("Failed to update project name")
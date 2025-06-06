from app.core.apikeys import generate_api_key, create_api_key_hashes
from app.schemas.projects import Projects
from app.dependencies.db import AsyncDB
from app.schemas.projects import ProjectAPIKey
from loguru import logger
from fastapi import HTTPException

async def create_initial_project(
    user_id: int, 
    project_name: str,
    organization_id: int, 
    db: AsyncDB
):
    try:
        async with db.transaction():
            # Create the organization
            created_project = await db.fetchrow(
                """
                INSERT INTO projects (name, organization_id)
                VALUES ($1, $2)
                RETURNING id, name, organization_id
                """,
                project_name,
                organization_id
            )

            # Add initial balance to organization
            await db.execute(
                """
                INSERT INTO project_balance (project_id, balance)
                VALUES ($1, 0.00000000)
                """,
                created_project["id"]
            )

            # Set the user project for resuming
            await db.execute(
                """
                UPDATE users
                SET last_selected_project_id = $1
                WHERE id = $2
                """,
                created_project["id"],
                user_id
            )
            return created_project
    except:
        raise Exception("Failed to create project")
    

async def create_new_project(
    user_id: int, 
    project_name: str,
    organization_id: int, 
    db: AsyncDB
):
    try:
        async with db.transaction():
            member_check = await db.fetchrow(
                """
                SELECT role FROM organization_members
                WHERE organization_id = $1 AND user_id = $2
                """,
                organization_id,
                user_id
            )
            
            if not member_check:
                raise HTTPException(status_code=403, detail="Not a member of this organization")
            
            num_projects_check = await db.fetchval(
                """
                SELECT COUNT(*)
                FROM projects
                WHERE organization_id = $1
                """,
                organization_id
            )
            if num_projects_check >= 100:
                raise HTTPException(
                    status_code=400,
                    detail="Organization has reached the maximum limit of 100 projects"
                )

            created_project = await db.fetchrow(
                """
                INSERT INTO projects (name, organization_id)
                VALUES ($1, $2)
                RETURNING id, name, organization_id
                """,
                project_name,
                organization_id
            )

            await db.execute(
                """
                INSERT INTO project_members (project_id, user_id, role)
                VALUES ($1, $2, 'admin')
                """,
                created_project['id'],
                user_id
            )

            await db.execute(
                """
                INSERT INTO project_balance (project_id, balance)
                VALUES ($1, 0.00000000)
                """,
                created_project['id']
            )

            # Set the user project for resuming
            await db.execute(
                """
                UPDATE users
                SET last_selected_project_id = $1
                WHERE id = $2
                """,
                created_project["id"],
                user_id
            )
            return created_project
    except:
        raise Exception("Failed to create project")


async def get_projects(organization_id: int, db: AsyncDB):
    try:
        organization_projects = await db.fetch(
            """
            SELECT *
            FROM projects
            WHERE organization_id = $1
            ORDER BY created_at DESC
            """,
            organization_id,
        )
        if not organization_projects:
            raise
        logger.info(organization_projects)
        return [Projects(**dict(project)) for project in organization_projects]
    except:
        raise Exception("Failed to get organization projects")
    

async def select_project(
    project_id: int,
    organization_id: int,
    user_id, 
    db: AsyncDB
):
    try:
        await db.execute(
            """
            UPDATE users
            SET last_selected_project_id = $1,
                last_selected_organization_id = $2
            WHERE id =$3
            """,
            project_id,
            organization_id,
            user_id,
        )
    except:
        raise Exception("Failed to select project")
    

async def list_project_api_keys(organization_id: int, project_id: int, db: AsyncDB):
    try:
        api_keys = await db.fetch(
            """
            SELECT 
                ak.*,
                p.name as project_name
            FROM api_keys ak
            LEFT JOIN projects p ON ak.project_id = p.id
            WHERE ak.organization_id = $1
            AND ak.project_id = $2 
            AND ak.is_active = TRUE
            ORDER BY ak.created_at DESC
            """,
            organization_id,
            project_id,
        )
        if api_keys:
            logger.info(f"Found user api keys: {api_keys}")
            return [ProjectAPIKey(**dict(key)) for key in api_keys]
        else:
            logger.info("No api keys found")
            return None
    except:
        raise Exception("Failed to get API keys")
    

async def create_project_api_key(
    api_key_name: str, 
    organization_id: int,
    project_id: int, 
    user_id: int, 
    db: AsyncDB
):
    api_key, key_prefix = generate_api_key()
    lookup_hash, hashed_api_key = create_api_key_hashes(api_key)
    try:
        record = await db.fetchrow(
            """
            INSERT INTO api_keys (
                name, 
                lookup_hash, 
                hashed_key, 
                user_id, 
                organization_id,
                project_id, 
                key_prefix
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *;
            """,
            api_key_name,
            lookup_hash,
            hashed_api_key,
            user_id,
            organization_id,
            project_id,
            key_prefix,
        )
        if record:
            logger.info(f"Created user: {record} api key: {api_key}")
            return {'api_key': api_key, 'record': ProjectAPIKey(**dict(record))}
        else:
            raise Exception("Failed to create user api key")
    except:
        raise Exception("Failed to create API key")
    

async def update_project_name(db: AsyncDB):
    try:
        updated_project_name = await db.fetchrow(
            """

            """
        )
        return Projects(**dict(updated_project_name))
    except:
        raise Exception("Failed to update project name")


async def get_project_members(db: AsyncDB):
    try:
        project_members = await db.fetch()
    except:
        raise Exception("Failed to get project members")


async def archive_project(db: AsyncDB):
    try:
        archived_project = await db.execute()
    except:
        raise Exception("Failed to archive project")
    
async def get_current_project(db: AsyncDB):
    try:
        current_project = await db.fetchrow(
            """
            SELECT *
            FROM 
            """
        )
    except:
        raise Exception("Failed to get current project")
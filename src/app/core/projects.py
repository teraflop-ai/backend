from app.schemas.projects import Projects
from app.dependencies.db import AsyncDB

async def create_project(
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
    

async def get_projects(organization_id: int, project_id: int, db: AsyncDB):
    try:
        organization_projects = await db.fetch(
            """
            SELECT *
            FROM projects
            WHERE organization_id = $1
            AND id = $2
            """,
            organization_id,
            project_id,
        )
        if not organization_projects:
            raise
        return [Projects(**dict(project)) for project in organization_projects]
    except:
        raise Exception("Failed to get organization projects")
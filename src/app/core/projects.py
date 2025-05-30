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
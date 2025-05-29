from app.dependencies.db import AsyncDB


async def create_organization(user_id, organization_name, db: AsyncDB):
    try:
        async with db.transaction():
            # Create the organization
            created_organization = await db.fetchrow(
                """
                INSERT INTO organizations (organization_name)
                VALUES ($1)
                RETURNING id, organization_name
                """,
                organization_name
            )

            # Add the user as admin
            await db.execute(
                """
                INSERT INTO organization_members (organization_id, user_id, role)
                VALUES ($1, $2, 'admin')
                """,
                created_organization["id"],
                user_id
            )

            # Add initial balance to organization
            await db.execute(
                """
                INSERT INTO organization_balance (organization_id, balance)
                VALUES ($1, 0.00000000)
                """,
                created_organization["id"]
            )

            # Set the user organization for resuming
            await db.execute(
                """
                UPDATE users
                SET last_selected_organization_id = $1
                WHERE id = $2
                """,
                created_organization["id"],
                user_id
            )
    except:
        raise Exception("Failed to create organization")
    

async def list_organization_members(db: AsyncDB):
    try:
        organization_members = await db.fetch(
            """
            SELECT *
            FROM organization_members
            WHERE organization_id = $1
            """,
        )
        if not organization_members:
            raise Exception("Could not find any members")
        return 
    except:
        raise Exception("Failed to get organization members")
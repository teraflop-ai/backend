from app.schemas.organizations import Organizations
from app.dependencies.db import AsyncDB
from app.schemas.organizations import OrganizationAPIKey
from loguru import logger

async def create_organization(user_id: id, organization_name: str, db: AsyncDB):
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
            return created_organization
    except:
        raise Exception("Failed to create organization")


async def check_if_member_exists(user_id: int, db: AsyncDB):
    """
    Checks to see if member is already part of an organization.
    """
    try:
        already_member = await db.fetchrow(
            """
            SELECT *
            FROM organization_members
            WHERE user_id = $1
            """,
            user_id
        )
        return already_member
    except:
        raise Exception("Failed to check if member exists")


async def list_organization_members(organization_id, db: AsyncDB):
    try:
        organization_members = await db.fetch(
            """
            SELECT *
            FROM organization_members
            WHERE organization_id = $1
            """,
            organization_id
        )
        if not organization_members:
            raise Exception("Could not find any members")
        return 
    except:
        raise Exception("Failed to get organization members")


async def get_organizations(organization_id: int, db: AsyncDB):
    try:
        organizations = await db.fetch(
            """
            SELECT *
            FROM organizations
            WHERE id = $1
            """,
            organization_id,
        )
        if not organizations:
            raise
        logger.info(organizations)
        return [Organizations(**dict(organization)) for organization in organizations]
    except:
        raise Exception("Failed to get organization projects")


async def select_organization(
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
    

async def list_organization_api_keys(organization_id: int, db: AsyncDB):
    try:
        api_keys = await db.fetch(
            """
            SELECT 
                ak.*,
                p.name as project_name
            FROM api_keys ak
            LEFT JOIN projects p ON ak.project_id = p.id
            WHERE ak.organization_id = $1 AND ak.is_active = TRUE
            ORDER BY ak.created_at DESC
            """,
            organization_id,
        )
        if api_keys:
            logger.info(f"Found user api keys: {api_keys}")
            return [OrganizationAPIKey(**dict(key)) for key in api_keys]
        else:
            logger.info("No api keys found")
            return None
    except:
        raise Exception("Failed to get API keys")

async def invite_member_to_organization():
    pass
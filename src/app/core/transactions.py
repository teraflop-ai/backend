import stripe
from datetime import date
from app.core.users import get_user_by_api_key
from app.schemas.organizations import (
    OrganizationBalance, 
    OrganizationTransactions, 
    OrganizationUsage,
)
from app.schemas.projects import (
    ProjectBalance, 
)
from app.dependencies.db import AsyncDB
from loguru import logger


def get_invoice_by_id(invoice_id):
    try:
        invoice = stripe.Invoice.retrieve(invoice_id)
        invoice_details = {
            'invoice_number': invoice.number,
            'invoice_url': invoice.hosted_invoice_url,
            'amount_paid': invoice.amount_paid / 100,
            'currency': invoice.currency,
        }
        logger.info(f"Invoice details: {invoice_details}")
        return invoice_details
    except:
        raise Exception("Failed to get invoice id")


async def increment_balance(
    amount, 
    invoice, 
    user_id: int, 
    organization_id: int,
    project_id: int,
    db: AsyncDB
):
    try:
        async with db.transaction():
            #verify project belongs to organization
            project_in_organization = await db.fetchval(
                """
                SELECT organization_id
                FROM projects
                WHERE id = $1
                """,
                project_id
            )
            if not project_in_organization:
                raise Exception("Could not find project id")
            
            if project_in_organization != organization_id:
                raise Exception("Project does not belong to organization")

            # update project balance
            update_project_balance = await db.fetchrow(
                """
                UPDATE project_balance
                SET balance = balance + $1, updated_at = CURRENT_TIMESTAMP
                WHERE project_id = $2
                RETURNING balance
                """,
                amount,
                project_id,
            )
            if not update_project_balance:
                raise Exception("Failed to update project balance")

            logger.info()

            # update organization balance
            update_organization_balance = await db.fetchrow(
                """
                UPDATE organization_balance
                SET balance = balance + $1, updated_at = CURRENT_TIMESTAMP
                WHERE organization_id = $2
                RETURNING balance
                """,
                amount,
                organization_id,
            )
            if not update_organization_balance:
                raise Exception(f"Failed to update balance for organization")
            
            logger.info(f"Incremented organization and project balance")

            # update user transactions
            status = "paid" if invoice.get("amount_paid") else "failed"

            transaction_record = await db.fetchrow(
                """
                INSERT INTO organization_transactions (
                    organization_id, 
                    user_id, 
                    amount, 
                    status, 
                    invoice_number, 
                    invoice_url
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                organization_id,
                user_id,
                amount,
                status,
                invoice.get("invoice_number"),
                invoice.get("invoice_url")
            )
            if not transaction_record:
                raise Exception("Failed to create transaction record")
            
            logger.info(f"Updated user transaction record {transaction_record}")

            return (
                ProjectBalance(**dict(update_project_balance)), 
                OrganizationBalance(**dict(update_organization_balance))
            )
    except:
        raise Exception("Failed to increment balance")


async def decrement_balance(api_key, amount, token_count, db: AsyncDB):
    try:
        async with db.transaction():

            user_id = await get_user_by_api_key(api_key, db)
            user_balance = await get_user_balance(user_id.user_id, db)
            if user_balance.balance < amount:
                raise Exception("User balance is less than amount to be deducted")

            user_usage = await update_user_usage(user_id, token_count, amount, db)
            logger.info(f"Updated user stats: {user_usage}")

            deduct_user_balance = await db.fetchrow(
                """
                UPDATE user_balance
                SET balance = balance - $1
                WHERE user_id = $2
                """,
                amount,
                user_id,
            )
            if not deduct_user_balance:
                raise Exception("Failed to deduct user balance")
            
            return deduct_user_balance
    except:
        raise Exception("Failed to decrement organization balance")


async def get_organization_transactions(organization_id: int, db: AsyncDB):
    try:
        organization_transactions = await db.fetch(
            """
            SELECT id, invoice_number, status, amount, created_at, invoice_url
            FROM organization_transactions
            WHERE user_id = $1
            """,
            organization_id
        )
        if not organization_transactions:
            logger.info("No previous organization transactions")
            return None
        return [OrganizationTransactions(**dict(transaction)) for transaction in organization_transactions]
    except:
        raise Exception("Failed to get organization transactions")


async def get_organization_balance(organization_id: int, db: AsyncDB):
    try:
        organization_balance = await db.fetchrow(
            """
            SELECT balance
            FROM organization_balance
            WHERE organization_id = $1
            """,
            organization_id
        )
        if not organization_balance:
            raise Exception("Organization balance not found")
        return OrganizationBalance(**dict(organization_balance))
    except:
        raise Exception("Failed to get organization balance")


async def get_project_balance(project_id: int, db: AsyncDB):
    try:
        project_balance = await db.fetch_row(
            """
            SELECT balance
            FROM project_balance
            WHERE project_id = $1
            """,
            project_id
        )
        if not project_balance:
            raise Exception("No project balance found")
        return ProjectBalance(**dict(project_balance))
    except:
        raise Exception("Failed to get project balance")


async def get_balances(project_id, organization_id, db: AsyncDB):
    try:
        async with db.transaction():
            project_balance = await db.fetch_row(
                """
                SELECT balance
                FROM project_balance
                WHERE project_id = $1
                """,
                project_id
            )
            if not project_balance:
                raise Exception("No project balance found")

            organization_balance = await db.fetchrow(
                """
                SELECT balance
                FROM organization_balance
                WHERE organization_id = $1
                """,
                organization_id
            )
            if not organization_balance:
                raise Exception("User balance not found")
    except:
        raise Exception("Failed to get balances")


async def get_organization_token_usage(organization_id: int, start_date: date, end_date:date, db: AsyncDB):
    try:
        organization_usage = await db.fetch(
            """
            SELECT id, organization_id, user_id, usage_date, token_count, request_count, total_spend
            FROM organization_token_usage
            WHERE organization_id = $1
            AND usage_date BETWEEN $2 and $3
            ORDER BY usage_date DESC
            """,
            organization_id,
            start_date,
            end_date
        )
        if not organization_usage:
            return []
        return [OrganizationUsage(**dict(usage)) for usage in organization_usage]
    except:
        raise Exception("Failed to get organization usage")


async def update_token_usage(user_id, token_count, amount, db: AsyncDB):
    try:
        user_usage = await db.fetchrow(
            """
            INSERT INTO user_token_usage (user_id, usage_date, token_count, request_count, total_spend)
            VALUES ($1, CURRENT_DATE, $2, 1, $3)
            ON CONFLICT (user_id, usage_date) 
            DO UPDATE SET 
                token_count = user_token_usage.token_count + $2,
                request_count = user_token_usage.request_count + 1,
                total_spend = user_token_usage.total_spend + $3,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
            """,
            user_id,
            token_count,
            amount
        )
        if not user_usage:
            raise Exception("User stats not found")
        return user_usage
    except:
        raise Exception("Failed to update user usage stats")
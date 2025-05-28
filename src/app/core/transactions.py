import stripe
from datetime import date
from app.core.users import get_user_by_api_key
from app.schemas.users import UserBalance, UserTransactions, UserUsage
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


async def increment_user_balance(amount, invoice, user_id: int, db: AsyncDB):
    try:
        async with db.transaction():
            # update user balance
            update_user_balance = await db.fetchrow(
                """
                UPDATE user_balance
                SET balance = balance + $1, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = $2
                RETURNING balance
                """,
                amount,
                int(user_id),
            )
            if not update_user_balance:
                raise Exception(f"Failed to update balance for user_id: {user_id}")
            
            logger.info(f"Incremented user balance {update_user_balance}")

            # update user transactions
            if invoice.get("amount_paid"):
                status = "paid"
            else:
                status = "failed"
            
            transaction_record = await db.fetchrow(
                """
                INSERT INTO user_transactions (user_id, amount, status, invoice_number, invoice_url)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                int(user_id),
                amount,
                status,
                invoice.get("invoice_number"),
                invoice.get("invoice_url")
            )
            if not transaction_record:
                raise Exception("Failed to create transaction record")
            
            logger.info(f"Updated user transaction record {transaction_record}")

            return UserBalance(**dict(update_user_balance))

    except Exception as e:
        logger.error("Failed to increment user balance")
        raise


async def decrement_user_balance(api_key, amount, token_count, db: AsyncDB):
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
    except Exception as e:
        raise


async def get_user_transactions(user_id: int, db: AsyncDB):
    try:
        user_transactions = await db.fetch(
            """
            SELECT id, invoice_number, status, amount, created_at, invoice_url
            FROM user_transactions
            WHERE user_id = $1
            """,
            user_id
        )
        if not user_transactions:
            logger.info("No previous User Transactions")
            return None
        
        logger.info(f"Found user api keys: {user_transactions}")
        return [UserTransactions(**dict(transaction)) for transaction in user_transactions]

    except:
        logger.error("Failed to get user transactions")
        raise


async def get_user_balance(user_id: int, db: AsyncDB):
    try:
        user_balance = await db.fetchrow(
            """
            SELECT balance
            FROM user_balance
            WHERE user_id = $1
            """,
            user_id
        )
        if not user_balance:
            raise Exception("User balance not found")
        logger.info(f"User balance: {user_balance}")
        return UserBalance(**dict(user_balance))
    except:
        logger.error("Failed to get user balance")
        raise


async def get_user_usage(user_id: int, start_date: date, end_date:date, db: AsyncDB):
    try:
        user_usage = await db.fetch(
            """
            SELECT id, user_id, usage_date, token_count, request_count, total_spend
            FROM user_token_usage
            WHERE user_id = $1
            AND usage_date BETWEEN $2 and $3
            ORDER BY usage_date DESC
            """,
            user_id,
            start_date,
            end_date
        )
        if not user_usage:
            return []
        return [UserUsage(**dict(usage)) for usage in user_usage]
    except:
        raise


async def update_user_usage(user_id, token_count, amount, db: AsyncDB):
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
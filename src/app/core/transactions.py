import stripe
from datetime import datetime
from app.schemas.users import UserBalance, UserTransactions
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


async def decrement_user_balance(amount, user_id: int, db: AsyncDB):
    try:
        async with db.transaction():
            await db.execute(
                """
                UPDATE user_balance
                SET balance = balance - $1
                WHERE user_id = $2
                """,
                amount,
                user_id,
            )
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
        if user_balance:
            logger.info(f"User balance: {user_balance}")
            return UserBalance(**dict(user_balance))
        else:
            logger.error("User balance not found")
            return {"balance": "not found"}
    except:
        logger.error("failed to get user balance")
        raise

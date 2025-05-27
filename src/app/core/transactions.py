from app.schemas.users import UserBalance
from app.dependencies.db import AsyncDB
from loguru import logger

async def increment_user_balance(amount, user_id: int, db: AsyncDB):
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
            transaction_record = await db.fetchrow(
                """
                INSERT INTO user_transactions (user_id, amount)
                VALUES ($1, $2)
                RETURNING *
                """,
                int(user_id),
                amount
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
        user_transactions = await db.fetchrow()
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

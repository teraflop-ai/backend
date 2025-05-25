from app.schemas.users import UserBalance
from app.dependencies.db import AsyncDB
from loguru import logger

async def increment_user_balance(amount, user_id: int, db: AsyncDB):
    try:
        # async with db.transaction():
        user_transaction = await db.fetchrow(
            """
            UPDATE user_balance
            SET balance = balance + $1
            WHERE user_id = $2
            RETURNING *
            """,
            amount,
            int(user_id),
        )
        if user_transaction:
            logger.info("Incremented user balance")
            return UserBalance(**dict(user_transaction))
        else:
            logger.warning("Warning")
            return None
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
            return user_balance
        else:
            logger.error("User balance not found")
            return {"balance": "not found"}
    except:
        logger.error("failed to get user balance")
        raise

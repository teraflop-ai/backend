from app.schemas.users import UserBalance
from app.dependencies.db import AsyncDB
from loguru import logger

async def increment_user_balance(amount, user_email, db: AsyncDB):
    try:
        async with db.transaction():
            user_transaction = await db.fetchrow(
                """
                UPDATE user_balance
                SET balance = balance + $1
                WHERE email = $2
                RETURNING *
                """,
                amount,
                user_email,
            )
            if user_transaction:
                logger.info("Success")
                return UserBalance(**dict(user_transaction))
            else:
                logger.warning("Warning")
                return None
    except Exception as e:
        logger.error("error")
        raise

async def decrement_user_balance(amount, user_email, db: AsyncDB):
    async with db.transaction():
        await db.execute(
            """
            UPDATE users
            SET balance = balance - $1
            WHERE id = $2
            """,
            amount,
            user_email,
        )

async def get_user_balance(user_id, db: AsyncDB):
    try:
        user_balance = db.fetchval(
            """
            SELECT balance
            FROM user_balance
            WHERE id = $1
            """,
            user_id
        )
        return user_balance
    except:
        raise

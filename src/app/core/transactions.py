from app.dependencies.db import AsyncDB

async def increment_balance(amount, user_id, db: AsyncDB):
    async with db.transaction():
        await db.execute(
            """
            UPDATE users
            SET balance = balance + $1
            WHERE id = $2
            """, 
            amount, 
            user_id
        )


async def decrement_balance(amount, user_id, db: AsyncDB):
    async with db.transaction():
        await db.execute(
            """
            UPDATE users
            SET balance = balance - $1
            WHERE id = $2
            """, 
            amount, 
            user_id
        )
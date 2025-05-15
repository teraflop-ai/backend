import stripe
from fastapi import Request, HTTPException
from loguru import logger
from app.dependencies.db import Client


async def get_stripe_customer(request: Request, asyncpg_client: Client):
    user_id = request.session.get("user_id")

    # check if stripe customer id exists
    # if it exists get stripe customer id from db
    # if it does not create stripe customer id and update db

    stripe_customer_id: str | None = None
    try:
        async with asyncpg_client.acquire() as connection:
            async with connection.transaction():
                stripe_customer_id = await connection.fetchval(
                    """
                    SELECT stripe_customer_id
                    FROM users
                    WHERE id = $1 
                    """,
                    user_id,
                )
    except Exception as e:
        raise

    if stripe_customer_id is not None:
        return stripe_customer_id

    else:
        try:
            stripe_customer = stripe.Customer.create()

            new_stripe_customer_id = stripe_customer.id
            logger.info(f"Created stripe customer {new_stripe_customer_id}")

        except Exception as e:
            raise

        try:
            async with asyncpg_client.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(
                        """
                        UPDATE users
                        SET stripe_customer_id = $1
                        WHERE user_id = $2
                        """,
                        new_stripe_customer_id,
                        user_id,
                    )
        except Exception as e:
            raise

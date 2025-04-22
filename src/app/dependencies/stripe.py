import stripe
from fastapi import HTTPException
from loguru import logger
from supabase import create_client, Client

async def get_stripe_customer(user_id: str):
    """
    """
    try:

        stripe_customer = stripe.Customer.create(

        )
        stripe_customer_id = stripe_customer.id
        logger.info(f"Created stripe customer {stripe_customer_id}")
        update_response = supabase.table("table_name")\
            .update() \
            .eq('user_id', user_id) \
            .execute()
        pass
    except:
        pass

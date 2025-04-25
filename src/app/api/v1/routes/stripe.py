import stripe
from typing import Optional
from stripe import Customer, checkout, error
from app.secrets.infisical import (STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET)
from slowapi.util import get_remote_address
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from fastapi.responses import RedirectResponse
import decimal
from app.dependencies.supabase import Client
from loguru import logger

domain_prefix = 'http://localhost:127.0.0.1'

payment_router = APIRouter(prefix="/payments", tags=["Payments"])

@payment_router.post("")
def create_checkout_session(request: Request):
    try:
        checkout_session = checkout.Session.create(
            customer="",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data":{
                            "name": "API Credits"
                        },
                        "unit_amount": 1, 
                    },
                    "quantity": 1,
                }
            ],
            success_url=domain_prefix + "",
            cancel_url=domain_prefix + "",
            mode="payment",
            automatic_tax={'enabled': True},

        )
        return RedirectResponse(
            checkout_session.url
        )
    except Exception as e:
        return HTTPException(403)

@payment_router.post("")
async def webhook_recieved(request_data, supabase: Client, stripe_signature: Optional[str] = Header(None)):
    
    payload = await request_data.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload=request_data,
            sig_header=stripe_signature,
            secret=""
        )
    except Exception as e:
        return
    
    event_type = event["type"]

    if event_type == "checkout.session.completed":
        logger.info("Completed checkout")

        # Get user balance
        """
        SELECT balance
        FROM users
        WHERE id = user_id
        LIMIT 1
        """
        
        current_balance = supabase.table() \
            .select("balance") \
            .eq("id", user_id) \
            .limit(1) \
            .single () \
            .execute()

        # Update user balance

        """
        CREATE OR REPLACE PROCEDURE
            update_balance(user_id BIGINT, amount NUMERIC)
        LANGUAGE plpgsql
        AS $$
        BEGIN ATOMIC
            UPDATE users
            SET balance = balance - amount
            WHERE id = user_id
        COMMIT
        END
        $$
        """

        update_balance = supabase.table("users") \
            .update({"balance", amount}) \
            .eq("id", user_id) \
            .execute()
    
    return


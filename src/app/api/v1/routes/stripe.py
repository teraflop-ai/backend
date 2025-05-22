import stripe
from typing import Optional
from stripe import checkout
from app.infisical.infisical import (
    # STRIPE_SECRET_KEY,
    # STRIPE_PUBLISHABLE_KEY,
    STRIPE_WEBHOOK_SECRET,
)
from slowapi.util import get_remote_address
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from fastapi.responses import RedirectResponse
import decimal

from app.core.transactions import (
    increment_user_balance, 
    get_user_balance
)
from app.dependencies.db import AsyncDB
from loguru import logger
from app.core.users import get_current_user
from app.schemas.users import User

domain_prefix = "http://localhost:127.0.0.1:8000"

payment_router = APIRouter(prefix="/payments", tags=["Payments"])


@payment_router.post("/create-checkout-session")
def create_checkout_session(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    try:
        amount_cents = int(request * 100)
        if amount_cents < 0:
            logger.error("Error")
            raise
        
        checkout_session = checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "API Credits",
                            "description": "",
                        },
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                }
            ],
            success_url=domain_prefix + "/payment-success?session_id={{}}",
            cancel_url=domain_prefix + "/payment-cancelled",
            mode="payment",
            automatic_tax={
                "enabled": True
            },
            metadata={
                "user_email": current_user.email,
                "amount": str(request.get(""))
            }
        )
        return RedirectResponse(checkout_session.url)
    except Exception as e:
        return HTTPException(403)


@payment_router.post("/webhook")
async def webhook_recieved(
    request_data: Request,
    db: AsyncDB,
    stripe_signature: Optional[str] = Header(None),
):
    payload = await request_data.body()

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, 
            sig_header=stripe_signature, 
            secret=STRIPE_WEBHOOK_SECRET.secretValue
        )
    except Exception as e:
        logger.info("Error")
        raise

    if event["type"] == "checkout.session.completed":
        session = event['data']['object']

        metadata = session.get("metadata")
        user_email = metadata.get("user_email")
        amount = metadata.get("amount")

        if session.get("payment_status") == "paid":
            try:
                # Update user balance in the db
                update_user_balance = increment_user_balance(
                    amount, user_email, db
                )
                if update_user_balance:
                    logger.info("User balance updated")
            except:
                logger.error("Error")
                raise
        else:
            logger.warning()

    elif event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
    return

@payment_router.get('/get-balance')
async def user_balance(
    db: AsyncDB,
    current_user = Depends(get_current_user)
):
    balance = await get_user_balance(current_user.id, db)
    print(balance)
    return balance
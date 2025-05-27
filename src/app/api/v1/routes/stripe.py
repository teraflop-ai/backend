import stripe
from typing import Optional
from stripe import checkout
from app.infisical.infisical import (
    STRIPE_SECRET_KEY,
    STRIPE_PUBLISHABLE_KEY,
    STRIPE_WEBHOOK_SECRET,
)
from fastapi import (
    APIRouter,
    Request, 
    HTTPException, 
    Header
)
import decimal
from app.core.transactions import (
    increment_user_balance, 
    get_user_balance
)
from app.dependencies.users import CurrentUser
from app.dependencies.db import AsyncDB
from loguru import logger
import os
from dotenv_vault import load_dotenv


load_dotenv()

stripe_price_id = os.getenv("STRIPE_PRICE_ID")

domain_prefix = "http://localhost:3000"

payment_router = APIRouter(prefix="/payments", tags=["Payments"])


@payment_router.post("/create-checkout-session")
async def create_checkout_session(current_user: CurrentUser):
    stripe.api_key = STRIPE_SECRET_KEY.secretValue
    try:
        checkout_session = checkout.Session.create(
            line_items=[
                {
                    "price": stripe_price_id,
                    "quantity": 1,
                }
            ],
            success_url=domain_prefix + "/dashboard/billing", #+ "/payment-success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_prefix + "/payment-cancelled",
            mode="payment",
            automatic_tax={
                "enabled": True
            },
            metadata={
                "user_id": str(current_user.id),
            }
        )
        logger.info(checkout_session.url)
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        return HTTPException(403)


@payment_router.post("/webhook")
async def webhook_received(
    request: Request,
    db: AsyncDB,
    stripe_signature: Optional[str] = Header(None),
):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, 
            sig_header=stripe_signature, 
            secret=STRIPE_WEBHOOK_SECRET.secretValue
        )
    except Exception as e:
        logger.info("Error")
        raise Exception("WEBHOOK FAILED")

    if event["type"] == "checkout.session.completed":
        session = event['data']['object']

        logger.info(f"Session data: {session}")

        metadata = session.get("metadata")
        logger.info(f"Metadata: {metadata}")
        user_id = metadata.get("user_id")
        amount_cents = session.get("amount_total")
        amount_dollars = decimal.Decimal(amount_cents) / decimal.Decimal('100')
        logger.info(f"Amount to add: {amount_dollars}")

        if session.get("payment_status") == "paid":
            try:
                update_user_balance = await increment_user_balance(
                    amount_dollars, 
                    user_id, 
                    db
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
    return {"status": "success"}


@payment_router.get('/get-balance')
async def user_balance(db: AsyncDB, current_user: CurrentUser):
    balance = await get_user_balance(current_user.id, db)
    logger.info(balance)
    formatted_balance = round(balance.balance, 2)
    return {"balance": formatted_balance} 
import stripe
from typing import Optional
from datetime import date
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
    Header,
    Query
)
import decimal
from app.core.transactions import (
    increment_balance, 
    get_organization_balance,
    get_organization_transactions,
    get_invoice_by_id,
    # get_user_usage
)
from app.dependencies.users import CurrentUser
from app.dependencies.db import AsyncDB
import msgspec
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
            invoice_creation={
                'enabled': True,
                'invoice_data': {
                    'description': 'Payment for account credits',
                    'custom_fields': [
                        {
                            'name': 'Purchase Type',
                            'value': 'Account Credits'
                        }
                    ],
                    'metadata': {
                        'organization_id': str(current_user.last_selected_organization_id),
                        'project_id': str(current_user.last_selected_project_id),
                        'user_id': str(current_user.id),
                        'purchase_type': 'credits'
                    },
                    'rendering_options': {
                        'amount_tax_display': 'include_inclusive_tax'
                    },
                    'footer': 'Thank you for your purchase!'
                }
            },
            metadata={
                'organization_id': str(current_user.last_selected_organization_id),
                'project_id': str(current_user.last_selected_project_id),
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

        invoice_id = session.get("invoice")
        if not invoice_id:
            raise Exception("Failed to generate invoice id")
        
        invoice = get_invoice_by_id(invoice_id)

        metadata = session.get("metadata")
        logger.info(f"Metadata: {metadata}")
        user_id = metadata.get("user_id")
        organization_id = metadata.get("organization_id")
        project_id = metadata.get("project_id")
        amount_cents = session.get("amount_total")
        amount_dollars = decimal.Decimal(amount_cents) / decimal.Decimal('100')
        logger.info(f"Amount to add: {amount_dollars}")

        if session.get("payment_status") == "paid":
            try:
                update_user_balance = await increment_balance(
                    amount_dollars,
                    invoice, 
                    int(user_id),
                    int(organization_id),
                    int(project_id), 
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
async def current_organization_balance(db: AsyncDB, current_user: CurrentUser):
    balance = await get_organization_balance(current_user.last_selected_organization_id, db)
    logger.info(balance)
    formatted_balance = round(balance.balance, 2)
    return {"balance": formatted_balance} 


@payment_router.get("/get-transaction-history")
async def current_organization_transaction_history(db: AsyncDB, current_user: CurrentUser):
    transaction_history = await get_organization_transactions(current_user.last_selected_organization_id, db)
    logger.info(f"Transaction History {transaction_history}")
    return msgspec.to_builtins(transaction_history)


# @payment_router.get("/get-user-usage")
# async def current_user_usage(
#     db: AsyncDB, 
#     current_user: CurrentUser,
#     start_date: date = Query(..., description="Start date for usage range"),
#     end_date: date = Query(..., description="End date for usage range")
# ):
#     user_usage = await get_user_usage(current_user.id, start_date, end_date, db)
#     return msgspec.to_builtins(user_usage)
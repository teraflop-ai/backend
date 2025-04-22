import stripe
from typing import Optional
from stripe import Customer, checkout, error
from app.secrets.infisical import (STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY)
from slowapi.util import get_remote_address
from fastapi import APIRouter, Depends, Request, HTTPException, Header
from fastapi.responses import RedirectResponse
import decimal
from app.database.supabase import create_supabase_client
from loguru import logger
from app.schemas.stripe import WebHookData

domain_prefix = ""

payment_router = APIRouter(prefix="/payments", tags=["Payments"])

@payment_router.get(
    "", 
    dependencies=[
        Depends(get_current_user()),
        Depends(create_supabase_client()),
        Depends(get_stripe_customer()),
    ]
)
@limiter.limit(
    "5/minute",
    key_func=get_remote_address
)
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

@payment_router.get("")
def webhook_recieved(request_data : WebHookData, stripe_signature: Optional[str] = Header(None)):
    
    if endpoint_secret:
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
        logger.info()
    
    return


import stripe
from stripe import Customer, checkout, error
from app.secrets.infisical import (STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY)

from fastapi import APIRouter, Depends

payment_router = APIRouter(prefix="/payments", tags=["Payments"])

@payment_router.get(
    "", 
    dependencies=[
        Depends(get_current_user()),
        Depends(get_db())
    ]
)
def create_payments():
    try:
        checkout_session = checkout.Session.create(

        )
    except Exception as e:
        return

@payment_router.get("", dependencies=[])
def webhook_recieved():
    pass
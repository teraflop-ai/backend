from stripe import Customer, checkout, error
from app.secrets.infisical import (STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY)

from fastapi import APIRouter, Depends

payment_router = APIRouter(prefix="/payments", tags=["Payments"])

@payment_router.get("")
async def create_payments():
    pass

from stripe import Customer, checkout, error
from app.infisical.infisical import (STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY)

from fastapi import APIRouter

router = APIRouter()

@router.get()
async def create_payments():
    pass

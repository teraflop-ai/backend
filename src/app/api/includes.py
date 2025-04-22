from fastapi import APIRouter
from app.api.v1.routes import auth, stripe, utils

api_router = APIRouter()

api_router.include_router(auth.auth_router)
api_router.include_router(stripe.payment_router)
api_router.include_router(utils.health_router)

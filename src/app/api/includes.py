from fastapi.responses import JSONResponse
from fastapi import APIRouter
from app.api.v1.routes import auth, users, stripe, utils

from typing import Any
import msgspec

class MsgSpecJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return msgspec.json.encode(content)

api_router = APIRouter(default_response_class=MsgSpecJSONResponse)

api_router.include_router(auth.auth_router)
api_router.include_router(users.user_router)
api_router.include_router(stripe.payment_router)
api_router.include_router(utils.health_router)

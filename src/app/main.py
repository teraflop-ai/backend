from fastapi import FastAPI
import valkey as redis
from starlette.middleware.sessions import SessionMiddleware
from app.secrets.infisical import SESSION_SECRET_KEY
from app.api.includes import api_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from app.database.db import async_manager

limiter = Limiter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_manager.async_connect()
    yield
    await async_manager.async_disconnect()

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY.secretValue)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
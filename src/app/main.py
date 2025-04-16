from fastapi import FastAPI
import valkey as redis
from fastapi_limiter import FastAPILimiter
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from app.secrets.infisical import SESSION_SECRET_KEY
from app.api.includes import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_connection = redis.from_url("redis://localhost:6379", encoding="utf8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    yield
    await redis_connection.aclose()

app = FastAPI(
    lifespan=lifespan
    # title=settings.PROJECT_NAME,
    # openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # generate_unique_id_function=custom_generate_unique_id,
)

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY.secretValue)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
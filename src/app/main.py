from fastapi import FastAPI
#from fastapi.routing import APIRoute
from starlette.middleware.sessions import SessionMiddleware
#from app.inifisical.infisical import SESSION_SECRET_KEY
#from app.api.includes import 

app = FastAPI(
    # title=settings.PROJECT_NAME,
    # openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # generate_unique_id_function=custom_generate_unique_id,
)

app.add_middleware(SessionMiddleware, secret_key="my-token")

# app.include_router()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
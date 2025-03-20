import os
import json
from authlib.integrations.starlette_client import OAuth, OAuthError
from dotenv_vault import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from infisical_sdk import InfisicalSDKClient
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

app = FastAPI()

client = InfisicalSDKClient(host="https://app.infisical.com")

client.auth.universal_auth.login(
    client_id=os.getenv("INFISICAL_CLIENT_ID"),
    client_secret=os.getenv("INFISICAL_CLIENT_SECRET"),
)

GOOGLE_CLIENT_ID = client.secrets.get_secret_by_name(
    secret_name="GOOGLE_CLIENT_ID",
    project_id=os.getenv("INFISICAL_PROJECT_ID"),
    environment_slug="dev",
    secret_path="/",
)

GOOGLE_CLIENT_SECRET = client.secrets.get_secret_by_name(
    secret_name="GOOGLE_CLIENT_SECRET",
    project_id=os.getenv("INFISICAL_PROJECT_ID"),
    environment_slug="dev",
    secret_path="/",
)

oauth = OAuth(
    config=Config(
        environ={
            "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID.secretValue,
            "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET.secretValue,
        }
    )
)

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

app.add_middleware(SessionMiddleware, secret_key="my-string")

@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')

@app.get("/login", name="login")
async def login_google(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/logout", name="logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")


@app.get("/auth", name="auth")
async def auth_google(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return e

    user = token.get("userinfo")
    if user:
        request.session["user"] = dict(user)
    return RedirectResponse(url="/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

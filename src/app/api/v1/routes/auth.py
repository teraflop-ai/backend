import json
from datetime import datetime, timedelta
from typing import Optional
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.config import Config
from app.secrets.infisical import (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
from jose import JWTError, jwt
from src.app.core.users import (
    get_user_by_email,
    get_user_by_google_id, 
    create_user
)

auth_router = APIRouter()

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
    client_kwargs={
        "scope": "openid email profile"
    },
)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@auth_router.get("/login")
async def login_google(request: Request):
    redirect_uri = request.url_for("auth_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")


@auth_router.get("/auth")
async def auth_google(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return e

    user_info = token.get("userinfo")
    if not user_info:
        raise

    user_email = user_info.get("email")
    user_google_id = user_info.get("sub")

    user = get_user_by_email(user_email)
    if not user:
        user = get_user_by_google_id(user_google_id)
    
    if user:
        pass
    else:
        # Create user
        user = create_user(user)

    token_expiration = timedelta(minutes=15)
    access_token = create_access_token(
        data={""},
        expires_delta=token_expiration
    )

    if user:
        request.session["user"] = dict(user)
    
    response = RedirectResponse(url="/dashboard")
    response.set_cookie(
        key="",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response
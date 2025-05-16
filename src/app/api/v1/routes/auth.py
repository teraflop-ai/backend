from fastapi import Depends
from datetime import timedelta
from loguru import logger
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from starlette.config import Config
from app.app_secrets.infisical import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.dependencies.db import AsyncDB
from app.core.users import (
    get_user_by_email,
    get_user_by_google_id,
    get_current_user,
    create_user,
    create_access_token,
)


ACCESS_TOKEN_EXPIRE_MINUTES = 15

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
    client_kwargs={"scope": "openid email profile"},
)


@auth_router.get("/login")
async def login_google(request: Request):
    redirect_uri = request.url_for("auth_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        # domain=".yourdomain.com"
    )
    return RedirectResponse(url="/")


@auth_router.get("/auth")
async def auth_google(request: Request, db: AsyncDB):
    # await google access token
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        logger.error("Unable to find get access token")
        return HTTPException()

    # get user info from token
    user_info = token.get("userinfo")
    if not user_info:
        logger.error("Could not get info from Google Oauth2 token")
        raise HTTPException()

    # get user email from user info
    user_email = user_info.get("email")
    if not user_email:
        logger.error("Could not find email from Google Oauth2 login")
        raise HTTPException()

    # get user from email
    user = get_user_by_email(user_email, db)
    logger.info(user)
    if not user:
        # Create new user if they do not exist
        logger.info("User does not exist. Creating user...")
        user = create_user(user_info, db)
        logger.info(user)

    # access token payload
    token_expiration = timedelta(minutes=15)
    access_token_payload = create_access_token(
        data={"sub": user.get("email")},
        expires_delta=token_expiration,
    )

    # redirect to user dashboard
    logger.info("Redirecting")
    response = RedirectResponse(url="/dashboard")

    # set auth cookie token
    logger.info("Setting authentication cookie")
    response.set_cookie(
        key="access_token",
        value=access_token_payload,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@auth_router.get("/users/me")
async def user_me(current_user = Depends(get_current_user)):
    return current_user
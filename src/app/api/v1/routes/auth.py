from datetime import timedelta
from loguru import logger
from authlib.integrations.starlette_client import OAuth, OAuthError
from authlib.common.security import generate_token
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from starlette.config import Config
from app.infisical.infisical import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.dependencies.db import AsyncDB
from app.core.users import (
    get_user_by_email,
    create_user,
    create_access_token,
    set_last_logged_in
)

FASTAPI_BACKEND_URL="http://localhost:8000"
NEXTJS_FRONTEND_URL="http://localhost:3000"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
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


@auth_router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = FASTAPI_BACKEND_URL + "/auth/google/callback/"
    code_verifier = generate_token(48)
    request.session["code_verifier"] = code_verifier
    return await oauth.google.authorize_redirect(
        request, 
        redirect_uri,
        code_challenge_method="S256",
        code_verifier=code_verifier
    )


@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        # domain=".yourdomain.com"
    )
    logger.info("Successfully logged out")


@auth_router.get("/google/callback")
async def auth_google_callback(request: Request, db: AsyncDB):
    logger.info(request.session)
    # await google access token
    try:
        code_verifier = request.session.get("code_verifier")
        if not code_verifier:
            logger.error("Code verifier not found in session")
            return RedirectResponse(url=f'{NEXTJS_FRONTEND_URL}/login?error=missing_verifier')

        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        logger.error(f"OAuth error during callback: {str(e)}")
        return RedirectResponse(url=f'{NEXTJS_FRONTEND_URL}/login?error={str(e)}')

    # clean up coder verifier data
    request.session.pop("code_verifier", None)

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
    user = await get_user_by_email(user_email, db)
    if user:
        logger.info(f"User found by email {user_email} : {user}")
        await set_last_logged_in(user, db)
    else:
        # Create new user if they do not exist
        logger.info("User does not exist. Creating user...")
        user = await create_user(user_info, db)
        if user:
            pass
        logger.info(f"Created user: {user}")

    # access token payload
    token_expiration = timedelta(minutes=15)
    access_token_payload = create_access_token(
        data={"sub": user.email},
        expires_delta=token_expiration,
    )

    # redirect to user dashboard
    logger.info("Redirecting")
    response = RedirectResponse(url=NEXTJS_FRONTEND_URL + "/dashboard/organization/general")

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



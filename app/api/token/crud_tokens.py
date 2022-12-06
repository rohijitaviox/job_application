from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status
)

from schema.tokens_schemas import (
    RequestAccessToken,
    RequestRefreshToken
)
from schema.user_schemas import UserSchema
from utils.auth.auth_tokens import AuthJWT
from utils.auth.auth import authenticate_user


async def access_token_crud(session: AsyncSession, body: RequestAccessToken):
    auth = AuthJWT(session=session)
    token_obj = await auth.validate_refresh_token(body.refresh_token, save_data=True)
    if token_obj == True:
        # get_access_token returns access token along with refresh token
        return await auth.get_access_token()
    elif token_obj.error == "expired":
        await auth.invalidate_refresh_token()
        # invalidate_refresh_token invalidates a single refresh token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, details="Refresh Token is invalid")
    elif token_obj.error == "rotated":
        await auth.invalidate_user_tokens(body.refresh_token)
        # invalidate_user_tokens invalidates all tokens of a user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, details="Refresh Token is invalid")


async def refresh_token_crud(session: AsyncSession, form_data: RequestRefreshToken):
    user: UserSchema = await authenticate_user(session, form_data.email, form_data.password)
    # authentcate_user authenticates and returns a user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    auth = AuthJWT(session)
    # No need to assign refresh token to a variable since we will store it in calss instance
    await auth.get_refresh_token(user.id, save_data=True)
    tokens = await auth.get_access_token(fresh_refresh_token=True)
    return tokens


async def invalidate_token_crud(session: AsyncSession, body: RequestAccessToken):
    auth = AuthJWT(session=session)
    return await auth.invalidate_refresh_token(body.refresh_token)
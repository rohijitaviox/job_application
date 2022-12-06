from typing import Union

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from schema.tokens_schemas import (
    RequestAccessToken,
    RequestRefreshToken,
    TokenResponse
)
from dependencies import get_db

from .crud_tokens import access_token_crud, refresh_token_crud


router = APIRouter(tags=["tokens"], prefix="/token")


@router.post("/access-token", response_model=TokenResponse)
async def access_token(payload: RequestAccessToken, session: AsyncSession = Depends(get_db)):
    """Endpoint for getting new access token"""
    return await access_token_crud(session, payload)


@router.post("/refresh-token", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def refresh_token(form_data: RequestRefreshToken, session: AsyncSession = Depends(get_db)):
    """Endpoint for getting new refresh token"""
    return await refresh_token_crud(session, form_data)


@router.post("/invalidate-token", status_code=status.HTTP_200_OK)
async def invalidate_token(payload: RequestAccessToken, session: AsyncSession = Depends(get_db)):
    return await invalidate_token_crud(sesison, payload)
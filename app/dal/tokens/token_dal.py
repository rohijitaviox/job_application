from uuid import UUID

from sqlalchemy import (
    select,
    delete
)
from sqlalchemy.ext.asyncio import AsyncSession

from models.accounts.tokens import OutstandingToken
from models.accounts.users import User
from utils.auth.token_objects import TokenData


class TokenDal:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_token(self, data: TokenData):
        token = OutstandingToken(
            jti=data.jti_uuid,
            token_type=data.token_type,
            expire_at=data.exp,
            user_id=data.get_user_id
        )
        self.session.add(token)
        await self.session.commit()

    async def delete_token(self, user_id: int, jti: UUID):
        stmt = delete(OutstandingToken).where(
            OutstandingToken.user_id == user_id, OutstandingToken.jti == jti)
        await self.session.execute(stmt)

    async def delete_user_tokens(self, user_id: int):
        stmt = delete(OutstandingToken).where(
            OutstandingToken.user_id == user_id)
        await self.session.execute(stmt)

    async def check_token_exists(self, user_id: int, jti: UUID):
        stmt = select(OutstandingToken).where(
            OutstandingToken.user_id == user_id, OutstandingToken.jti == jti)
        return await self.session.scalar(statement=stmt)

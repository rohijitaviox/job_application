from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import (
    select,
    delete,
)

from models.accounts.users import User
from utils.auth.passwords import get_password_hash, verify_password


class UserDal:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, **user_data):
        if {"name", "email", "password"} != set(user_data.keys()):
            raise ValueError("'name', 'email' and 'password' are required.")
        user_data['password'] = get_password_hash(user_data['password'])
        user_data.setdefault("active", True)
        user = User(
            **user_data
        )
        self.session.add(user)
        await self.session.commit()

    async def get_user_by_email(self, email: str) -> User:
        stmt = select(User).where(User.email == email)
        return await self.session.scalar(stmt)

    async def get_user_by_id(self, user_id: int) -> User:
        stmt = select(
            User.id, User.name, User.email
        ).where(User.id == user_id)
        return await self.session.scalar(stmt)

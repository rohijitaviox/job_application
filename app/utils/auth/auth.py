from sqlalchemy.ext.asyncio import AsyncSession
from dal.users.user_dal import UserDal
from utils.auth.passwords import verify_password
from schema.user_schemas import UserSchema


async def authenticate_user(session: AsyncSession, email: str, password: str):
    user_dal = UserDal(session=session)
    user = await user_dal.get_user_by_email(email)
    if user is None or not user.active:
        return False
    return UserSchema(id=user.id, name=user.name, email=user.email) if verify_password(user.password, password) else False

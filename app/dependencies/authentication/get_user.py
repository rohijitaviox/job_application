from typing import Union

from fastapi.security import OAuth2PasswordBearer
from fastapi import Header, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession

from utils.auth.auth_tokens import AuthJWT
from dependencies.db.db_dependency import get_db
from dal.users.user_dal import UserDal


async def get_current_user_id(www_authentication: str = Header(), session: AsyncSession = Depends(get_db)):
    auth = AuthJWT(session)
    return await auth.validate_access_token(www_authentication)


async def get_current_user(user_id: Union[int, None] = Depends(get_current_user_id),session:AsyncSession=Depends(get_db)):
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = await UserDal(session).get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        return user
    

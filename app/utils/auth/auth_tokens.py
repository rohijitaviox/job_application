from typing import Union
from datetime import timedelta, datetime
from uuid import uuid4


from jwt import encode, decode,PyJWTError
from sqlalchemy.orm import Session

from config import PRIVATE_ENC_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRES_MINUTES, REFRESH_TOKEN_EXPIRES_DAYS, ROTATE_REFRESH_TOKENS, AUTHENTICATE_FROM_DB
from dal.tokens.token_dal import TokenDal
from .token_objects import TokenData, TokenError


class AuthJWT:
    def __init__(self, session: Session):
        self.session = session
        self.__data = None
        self.__refresh_token = None

    # Decoded Data
    def set_data(self, data: TokenData):
        self.__data = data

    @property
    def get_data(self):
        return self.__data

    def delete_date(self):
        self.__data = None

    # Refresh Token
    def set_refresh_token(self, refresh_token: str):
        self.__refresh_token = refresh_token

    @property
    def get_saved_refresh_token(self):
        return self.__refresh_token

    def delete_refresh_token(self):
        self.__refresh_token = None

    # Methods
    def create_token_data(self, data: dict, token_type: str) -> TokenData:
        """Create a dictionary with all data required for a token"""
        current_time = datetime.utcnow()
        data['iat'] = current_time
        data['token_type'] = token_type
        data['jti'] = uuid4().hex
        if token_type == "access":
            data['exp'] = current_time + \
                timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        elif data['token_type'] == "refresh":
            data['exp'] = current_time + \
                timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS)
        return TokenData(**data)

    def encode_token(self, data: TokenData):
        """Create a jwt token"""
        to_encode = data.dict().copy()
        encoded_jwt = encode(
            to_encode, PRIVATE_ENC_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str):
        """Decode a jwt token to produce a dict"""
        data = decode(
            token, PRIVATE_ENC_KEY, algorithms=ALGORITHM)
        return TokenData(**data)

    async def validate_access_token(self, access_token: str):
        """Validate an access token and return user id. If `AUTHENTICATE_FROM_DB` is True, token will be validated from DB, else not.
        :param access_token: Access token in header `WWW-Authentication`
        """
        try:
            data = self.decode_token(access_token)
        except PyJWTError:
            return None
        if not data.token_type == "access":
            return None
        if AUTHENTICATE_FROM_DB:
            token_dal = TokenDal(session=self.session)
            token_exists = await token_dal.check_token_exists(data.get_user_id, data.jti_uuid)
            return None if not token_exists else data.get_user_id
        return data.get_user_id

    async def validate_refresh_token(self, refresh_token: str, save_data: bool = False) -> Union[TokenError, bool]:
        """
        Validate a refresh token. Returns True if token is valid.\n
        If token invalid, returns a TokenError object.

        :param save_data: Flag, if set to true, saves the refresh_token decoded data to the AuthJWT instance
        """
        try:
            data = self.decode_token(refresh_token)
        except PyJWTError:
            return TokenError("expired")
        # ====================
        if data.token_type == "refresh" and save_data:
            self.set_data(data)
            self.set_refresh_token(refresh_token)
        # TODO: Chek if token exists
        token_dal = TokenDal(self.session)
        token_exists = await token_dal.check_token_exists(
            data.get_user_id, data.jti_uuid)
        if token_exists is None:
            return TokenError("rotated")
        else:
            return True

    async def invalidate_refresh_token(self, refresh_token: str = None):
        """
        Invalidate Refresh tokens. Delete refresh tokens from Database.

        :param refresh_token: Refresh token to be invalidated.
         If None, there must be a refresh token saved in class instance.
        """
        if refresh_token is None and self.get_saved_refresh_token is None:
            raise ValueError(
                "Current class instance has no refresh token. Refresh token required")
        data = None
        if refresh_token:
            # TODO: Check for errors
            data = self.decode_token(refresh_token)
        else:
            data = self.get_data
        # delete from db
        token_dal = TokenDal(self.session)
        await token_dal.delete_token(data.get_user_id, data.jti_uuid)

    async def invalidate_user_tokens(self, refresh_token: str = None):
        """
        Invalidate all tokens of a user.

        :param refresh_token: Refresh token. The user it belongs to will have all their tokens invalidated
        """
        data = self.get_data if refresh_token is None else self.decode_token(
            refresh_token)
        token_dal = TokenDal(self.session)
        await token_dal.delete_user_tokens(data.get_user_id)

    async def get_refresh_token(self, user_id: int, save_data: bool = False):
        """
        Create and return a new refresh token.\n
        :param user_id: User id for which new refresh token is to be created.
        :param save_data: If set to True, sill save resultant data to the class instance.
        """
        data = {
            "user_pk": user_id
        }
        data = self.create_token_data(data, "refresh")
        # Save in database
        token_dal = TokenDal(self.session)
        await token_dal.create_token(data)
        refresh_token = self.encode_token(data)

        if save_data:
            self.set_data(data)
            self.set_refresh_token(refresh_token)
        return refresh_token

    async def rotate_refresh_token(self, refresh_token: str = None):
        """
        Rotate refresh tokens by invalidating given/current refresh tken and returning new one
        :param refresh_token: Refresh token to be rotated.  
        If None, refresh token saved to current class instance will be used.
        """
        if not refresh_token and not self.get_saved_refresh_token:
            raise ValueError(
                "Current class instance has no refresh token. Refresh token required.")
        save_data = bool(refresh_token)
        data = self.get_data if refresh_token is None else self.decode_token(
            refresh_token)
        user_id = data.get_user_id
        self.invalidate_refresh_token(refresh_token)
        refresh_token = self.get_refresh_token(user_id, save_data=save_data)
        return refresh_token

    async def get_access_token(self, refresh_token: str = None, fresh_refresh_token: bool = False):
        """
        Create and get an access token. If refresh_token specified, it will be used to create a new access token. \n
        Otherwise, if AuthJWT class has been used to validate a refresh_token, the saved data from that refresh token would be used. \n
        If neither exists, ValueError will be raised.
        If ROTATE_REFRESH_TOKEN is set to true in config, a new refresh token will also be created and returned.

        :param refresh_token: Refresh Token that will be used to create a new access token.\n
        :param fresh_refresh_token: Flag, if set to True, signifies that refresh_token being given is fresh and needs tot be rotated.
        """
        # Raise error if no refresh token
        if refresh_token is None and self.get_saved_refresh_token is None:
            raise ValueError(
                "Current class instance has no refresh token. Refresh token required.")
        data = None
        if refresh_token:
            data = self.decode_token(refresh_token)
        else:
            data = self.get_data
            refresh_token = self.get_saved_refresh_token
        access_token_data = {
            "user_pk": data.get_user_id
        }
        access_token_data = self.create_token_data(access_token_data, "access")
        access_token = self.encode_token(access_token_data)

        # If AUTHENTICATE_FROM_DB, save access token data in database
        if AUTHENTICATE_FROM_DB:
            token_dal = TokenDal(self.session)
            await token_dal.create_token(access_token_data)

        # If Refresh tokens are to be rotated
        if not fresh_refresh_token and ROTATE_REFRESH_TOKENS:
            data = None
            refresh_token = self.rotate_refresh_token(
                None if self.get_saved_refresh_token else refresh_token
            )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

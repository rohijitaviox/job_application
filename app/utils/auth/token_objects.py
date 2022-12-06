from uuid import UUID
from datetime import datetime
from typing import Union, Optional

from pydantic import (
    BaseModel,
    validator,
    ValidationError
)

class TokenData(BaseModel):
    def __init__(__pydantic_self__, **data) -> None:
        data["__user_pk"] = data['user_pk']
        data['user_pk'] = __pydantic_self__.hash_data(data['user_pk'])
        super().__init__(**data)

    __user_pk: int
    user_pk: str
    jti: str
    token_type: str
    iat: datetime
    exp: datetime

    @property
    def jti_uuid(self):
        return UUID(self.jti)

    @property
    def get_user_id(self):
        return self.__user_pk

    @property
    def get_exp_time(self):
        return datetime.strptime(self.exp, "%Y-%-m-%-d")

    @validator("token_type")
    def token_type_validator(cls, token_type):
        allowed_types = ["access", "refresh"]
        if token_type not in allowed_types:
            raise ValidationError(
                "token type should be either 'access' or 'refresh'")
        return token_type

    def dict(self, *, include: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = None,
             exclude: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = None, by_alias: bool = False,
             skip_defaults: Optional[bool] = None, exclude_unset: bool = False, exclude_defaults: bool = False,
             exclude_none: bool = False) -> 'DictStrAny':
        data: dict = super().dict(include, exclude, by_alias, skip_defaults,
                                  exclude_unset, exclude_defaults, exclude_none)
        data["user_pk"] = data["__user_pk"]
        data.__delattr__("__user_pk")
        return data

    @staticmethod
    def hash_data(data: Union[str, int]):
        # TODO: Implement hashing
        return str(data)

    @staticmethod
    def unhash_data(hashed_data: str):
        # TODO: IMplement unhashing
        if hashed_data.isdigit:
            return int(hashed_data)
        else:
            return hashed_data


class TokenError(BaseModel):
    error: str

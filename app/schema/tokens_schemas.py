from pydantic import BaseModel


class RequestAccessToken(BaseModel):
    refresh_token: str


class RequestRefreshToken(BaseModel):
    email:str
    password:str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

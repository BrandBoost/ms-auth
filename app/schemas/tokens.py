from pydantic import BaseModel, Field


class RefreshToken(BaseModel):
    refresh_token: str


class AccessToken(RefreshToken):
    access_token: str


class ObtainTokenResponseSchema(BaseModel):
    access_token: str = Field(description='Access token')
    refresh_token: str = Field(description='Refresh token')
    access_token_expire: int = Field(description='Access token expire time in minutes')
    refresh_token_expire: int = Field(description='Refresh token expire time in minutes')


class Token(AccessToken):
    ...

import jwt
import typing as tp

from fastapi.exceptions import HTTPException

from datetime import timedelta, datetime

from app.config import settings
from app.schemas.tokens import ObtainTokenResponseSchema

TOKEN_CREATE_HELPING_DATA: tp.Any = {
    'refresh': {
        'expire': settings.JWT_REFRESH_TTL,
        'subject': settings.REFRESH_TOKEN_JWT_SUBJECT
    },
    'access': {
        'expire': settings.JWT_ACCESS_TTL,
        'subject': settings.ACCESS_TOKEN_JWT_SUBJECT
    }
}


async def create_token(token_type: str, user_id: str) -> str:
    """ Create access token using credentials or refresh token """

    expire = datetime.utcnow() + timedelta(minutes=float(TOKEN_CREATE_HELPING_DATA[token_type]['expire']))

    payload = {
        'id': user_id,
        'exp': expire,
        'sub': TOKEN_CREATE_HELPING_DATA[token_type]['subject'],
    }
    encoded_jwt: str = jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def create_tokens(user_id: str) -> ObtainTokenResponseSchema:
    """ Create tokens """

    access_token = await create_token(token_type='access', user_id=user_id)
    refresh_token = await create_token(token_type='refresh', user_id=user_id)

    return_data: tp.Dict[str, tp.Any] = {
        'refresh_token': refresh_token,
        'access_token': access_token,
        'access_token_expire': settings.JWT_ACCESS_TTL,
        'refresh_token_expire': settings.JWT_REFRESH_TTL,
    }
    return ObtainTokenResponseSchema(**return_data)


async def generate_access_token_from_refresh(refresh_token: str) -> tp.Dict[str, tp.Any]:
    """
    Generate access token from refresh token
    Args:
        refresh_token: refresh_token
    Return:
        dict with access token
    """

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])  # type: ignore

        if payload['sub'] != settings.REFRESH_TOKEN_JWT_SUBJECT:
            raise HTTPException(status_code=401, detail='Refresh token is expected')
        return_data = await create_tokens(user_id=payload['id'])
        return return_data.dict()
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token or token is expired')

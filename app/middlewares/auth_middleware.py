import json
import jwt
import typing as tp

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request

from app.config import settings


async def authenticate(request: Request) -> tp.Tuple[bool, tp.Dict[str, str]]:
    """
    Decorator for authenticate user(set current user to request)
    """

    token_components = request.headers.get("Authorization", '').split(' ')
    token_type = token_components[0]
    access_token = token_components[-1]

    if token_type != settings.TOKEN_TYPE:
        return False, {'token': 'Invalid token type'}

    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload['sub'] != settings.ACCESS_TOKEN_JWT_SUBJECT:
            return False, {'error': 'Access token is expected'}

        request.state.user_id = payload['id']
        return True, {}
    except Exception:
        request.state.user_id = None
        return False, {'error': 'Invalid token or token is expired'}


class ApiKeyMiddleware(BaseHTTPMiddleware):
    authorize_paths = [
        '/api/v1/users/me/',
        '/api/v1/media/me/avatar/'
    ]

    async def dispatch(self, request: Request, call_next: tp.Any) -> tp.Any:
        if request.url.path in self.authorize_paths and request.method != 'OPTIONS':
            is_valid, error_message = await authenticate(request=request)
            if not is_valid:
                return Response(content=json.dumps(error_message), status_code=401)
        else:
            # TODO check and mb add set full user model
            request.state.user_id = "1"
        return await call_next(request)

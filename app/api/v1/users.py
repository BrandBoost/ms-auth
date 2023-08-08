import typing as tp

from datetime import datetime

from fastapi import APIRouter, Request, UploadFile

from app.config import logger  # noqa
from app.enums import UserRole
from app.schemas import (
    BaseUserRead as BaseUserReadSchema,
    LegalUserCreateUpdate as CreateUpdateRegularUserSchema,
    PrivateUserCreateUpdate as CreateUpdatePrivateUserSchema,
    RefreshToken as RefreshTokenSchema,
    Login as LoginSchema,
    Token as TokenSchema,
    Email as EmailSchema,
    ResetPasswords as ResetPasswordsSchema,
    RetrieveLogin as RetrieveLoginSchema,
    PrivateUserCreate,
    LegalUserCreate,
)
from app.schemas.tokens import ObtainTokenResponseSchema
from app.schemas.users import PatchUserUpdateRequest, UploadAvatarResponse
from app import services

user_routes = APIRouter()


@user_routes.get("/me/", status_code=200, response_model=BaseUserReadSchema)
async def get_user(request: Request):
    return await services.get_user_by_id(user_id=request.state.user_id)


@user_routes.patch("/me/", status_code=200, response_model=BaseUserReadSchema)
async def update_user_me(request: Request, body: PatchUserUpdateRequest):
    return await services.update_user(user_id=request.state.user_id, instance=body)


@user_routes.patch(
    "/me/avatar/",
    status_code=200,
    response_model=UploadAvatarResponse
)
async def upload_avatar(request: Request, file: UploadFile) -> tp.Dict[str, tp.Any]:
    return await services.save_user_avatar_image(user_id=request.state.user_id, body=file)


@user_routes.post("/private_person/register/", status_code=201, response_model=ObtainTokenResponseSchema)
async def register_private_person(data: PrivateUserCreate) -> tp.Dict[str, tp.Any]:
    person = CreateUpdatePrivateUserSchema(
        role=UserRole.PRIVATE_PERSON,
        is_verified=False,
        created_at=datetime.now(), **data.dict()
    )
    user = await services.create_user(person=person)
    tokens = await services.create_tokens(user_id=str(user.get("_id")))
    return tokens.dict()


@user_routes.post("/legal_person/register/", status_code=201, response_model=TokenSchema)
async def register_legal_person(data: LegalUserCreate):
    # todo: switch on after server's adjusting
    # data.additional_info = await self.services.collect_additional_info(data.additional_info.dict())
    person = CreateUpdateRegularUserSchema(role=UserRole.LEGAL_PERSON, is_verified=False,
                                           created_at=datetime.now(), **data.dict())
    user = await services.create_user(person=person)
    return await services.create_tokens(user_id=str(user.get("_id")))


@user_routes.post("/login/", response_model=RetrieveLoginSchema, status_code=200)
async def login(data: LoginSchema):
    return await services.login_user(data=data)


@user_routes.post("/forgot_password/", status_code=200)
async def forgot_password(email: EmailSchema):
    await services.forgot_password(email=email)


@user_routes.post("/reset_password/", status_code=200)
async def reset_password(data: ResetPasswordsSchema):
    return await services.reset_password(data=data)


@user_routes.post("/activate/{user_id}/", status_code=200)
async def activate_person(user_id: str):
    # todo: activate person in registration and add restrictions for unferifed user
    await services.activate_person(user_id=user_id)


@user_routes.post("/refresh_token/", response_model=TokenSchema, status_code=200)
async def refresh_token(token: RefreshTokenSchema):
    return await services.generate_access_token_from_refresh(refresh_token=token.refresh_token)


@user_routes.post("/check_inn/", status_code=200)
async def check_company_by_inn(inn: str):
    await services.check_exist_company_by_inn(inn)

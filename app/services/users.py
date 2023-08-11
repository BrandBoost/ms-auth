import os
import json
import secrets
import aiohttp
import typing as tp
import jwt
from fastapi import HTTPException, UploadFile
from pillow import Image
from datetime import datetime, timedelta
from bson import ObjectId
from passlib.context import CryptContext

from app.config import settings, logger
from app.repositories import UsersRepository, ProjectsRepository
from app.schemas import (
    Token as TokenSchema,
    Login as LoginSchema,
    RefreshToken as RefreshTokenSchema,
    Email as EmailSchema,
    ResetPasswords as ResetPasswordsSchema,
    RetrieveLogin as RetrieveLoginSchema,
)
from app import services
from app.schemas.users import PatchUserUpdateRequest
from app.services.emails import get_email_verify_render

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def append_to_json_file(file_name, expire_date, _id, secure_number):
    try:
        with open(file_name, "r") as file:
            data = dict(json.load(file))

        data[secure_number] = [expire_date, _id]
        with open(file_name, "w") as file:
            json.dump(data, file)
    except FileNotFoundError:
        data_test = []
        with open(file_name, "w") as file:
            json.dump(data_test, file)


async def read_secure_number(file_name, secure_number):
    # TODO refactor
    with open(file_name, "r") as file:
        data = json.load(file)

    if secure_number not in data:
        raise HTTPException(status_code=409, detail="Invalid secure number.")

    expire_date, _id = data[secure_number]
    if datetime.now() > datetime.fromisoformat(expire_date):
        raise HTTPException(status_code=409, detail="Secure number has expired.")
    return _id


async def email_verify(email: str):
    to_encode = {"email": email}
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_REFRESH_TTL)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    confirmation_url = (
        f"http://127.0.0.1:8000/api/v1/users/verify/?confirm_code={encoded_jwt}"
        # f"{settings.SERVICE_URL}/api/v1/users/verify/?confirm_code={confirmation_code}"
    )
    render = await get_email_verify_render(email, confirmation_url)
    await services.send_mail(email=email, content=render)


async def verify_user_email(confirm_code: str):
    try:
        payload = jwt.decode(
            confirm_code, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        await UsersRepository().update_status_by_email(email=payload.get("email"))
    except jwt.ExpiredSignatureError as exc:
        logger.exception(exc)
        raise HTTPException(
            status_code=401, detail={"error": "Invalid token or token is expired"}
        )
    except Exception as exc:
        logger.exception(exc)
        raise HTTPException(status_code=500, detail={"error": "Internal server error"})


async def get_user_by_id(user_id: str) -> dict:
    return await UsersRepository().get_by_id(_id=ObjectId(user_id))  # type: ignore


async def save_user_avatar_image(
    user_id: str, body: UploadFile
) -> tp.Dict[str, tp.Any]:
    try:
        user = await UsersRepository().get_by_id(ObjectId(user_id))
        if user and user.get("avatar_link"):
            file_path = user["avatar_link"]
            if os.path.exists(file_path):
                os.remove(file_path)
            thumbnail_path = user.get("avatar_thumbnail_link")
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        file_name = str(body.filename).replace(" ", "_")
        file_path = os.path.join("uploads", file_name)
        with open(file_path, "wb") as f:
            f.write(body.file.read())

        file_path = file_path.replace("\\", "/")

        # Создание и сохранение thumbnail (40x40)
        thumbnail_path = os.path.join("uploads", f"thumbnail_{file_name}")
        with Image.open(file_path) as img:
            img.thumbnail((40, 40))
            img.save(thumbnail_path)

        # Создание и сохранение основного изображения (236x236)
        main_image_path = os.path.join("uploads", f"main_{file_name}")
        with Image.open(file_path) as img:
            img.thumbnail((236, 236))
            img.save(main_image_path)

        await UsersRepository().update_by_id(
            ObjectId(user_id),
            {"avatar_link": main_image_path, "avatar_thumbnail_link": thumbnail_path},
        )

        main_image_link = f"{settings.SERVICE_URL}/{main_image_path}/"
        thumbnail_link = f"{settings.SERVICE_URL}/{thumbnail_path}/"
        return {"avatar_link": main_image_link, "avatar_thumbnail_link": thumbnail_link}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_user(
    user_id: str, instance: PatchUserUpdateRequest
) -> tp.Dict[tp.Any, tp.Any] | None:
    data = instance.dict(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="Bad request.")

    await UsersRepository().update_by_id(instance_id=ObjectId(user_id), instance=data)
    return await UsersRepository().get_by_id(_id=ObjectId(user_id))


async def create_user(person) -> dict:
    await UsersRepository().delete_by_id(ObjectId("64d651482990268595d59574"))
    user = await UsersRepository().get_by_email(email=person.email)
    person.password = pwd_context.hash(person.password)
    if user:
        raise HTTPException(
            status_code=409, detail="User with such email already exists"
        )
    user = await UsersRepository().create(instance=person.dict())
    await email_verify(person.email)
    return user


async def login_user(data: LoginSchema) -> TokenSchema:
    user = await UsersRepository().get_by_email(email=data.email)
    if user is None:
        raise HTTPException(status_code=404, detail="No such user with chosen email.")

    if not pwd_context.verify(data.password, user.get("password")):
        raise HTTPException(status_code=401, detail="Incorrect credentials.")

    if not user.get("is_verified"):
        raise HTTPException(status_code=401, detail="You need to confirm your email")

    tokens = await services.create_tokens(user_id=str(user.get("_id")))
    return RetrieveLoginSchema(user=user, **tokens.dict())


async def check_exist_company_by_inn(tin: str) -> dict:
    """
    :param tin: Taxpayer Identification Number
    :return: True if there is an entry in the registry with this TIN, else return False
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api-fns.ru/api/egr?req={tin}&key={settings.API_FNS_KEY}"
        ) as response:
            # TODO: Fix the description
            if response.status == 403:
                raise HTTPException(
                    status_code=500,
                    detail="I'll fix the description later, if I threw it out, "
                    "then it means you can't make a request to the api-fns",
                )
            company_exist = await response.json()
            data = company_exist.get("items", None)
            if data is None or data == []:
                raise HTTPException(
                    status_code=404, detail="There no company with such TIN."
                )
            return data


async def collect_additional_info(additional_info: dict):
    data = await check_exist_company_by_inn(tin=additional_info.get("inn", None))
    juridical_person = data[0]["ЮЛ"]
    name = juridical_person["НаимСокрЮЛ"]
    full_name = juridical_person["Руководитель"]["ФИОПолн"]
    address = juridical_person["Адрес"]["АдресПолн"]
    return {"name": name, "head": full_name, "address": address} | additional_info


async def forgot_password(email: EmailSchema):
    secure_number = secrets.randbelow(1000000)
    secure_number_str = f"{secure_number:06}"

    # TODO move to depends
    user = await UsersRepository().get_by_email(email=email.email)
    if user is None:
        raise HTTPException(status_code=404, detail="No such user with chosen email.")

    expire_date = datetime.now() + timedelta(minutes=30)
    await append_to_json_file(
        "reset_passwords.json",
        str(expire_date),
        str(user.get("_id")),
        secure_number_str,
    )

    user_first_name = str(user.get("additional_info")["first_name"])
    await services.send_mail(
        email=email.email,
        content=f"{await services.open_html(str(user.get('email')), user_first_name, secure_number_str, email.is_change)}",
    )


async def reset_password(data: ResetPasswordsSchema):
    _id = await read_secure_number(
        "reset_passwords.json", secure_number=data.secure_code
    )
    user = await get_user_by_id(user_id=_id)
    user["password"] = pwd_context.hash(data.password)
    await UsersRepository().update_by_id(ObjectId(_id), user)


async def activate_person(user_id: str):
    # TODO add fastapi Depends(404 status code will be returned)
    instance = await get_user_by_id(user_id=user_id)
    instance["is_verified"] = True
    await UsersRepository().update_by_id(
        instance_id=ObjectId(user_id), instance=instance
    )


async def delete_person(user_id: str):
    await UsersRepository().delete_by_id(_id=ObjectId(user_id))
    await UsersRepository().delete_user_parsers(owner_id=ObjectId(user_id))
    await ProjectsRepository().delete_all_user_projects(owner_id=ObjectId(user_id))
    return {"result": f"User {user_id} sucessfully deleted"}


async def get_user_by_token(self, authorization: str) -> dict:
    user_id = await self.tokens.decode_access_jwt_token(authorization=authorization)
    return await self.get_user_by_id(user_id=user_id)


async def refresh_token(self, token: RefreshTokenSchema) -> TokenSchema:
    user_id = await self.tokens.decode_refresh_jwt_token(
        refresh_token=token.refresh_token
    )
    return await self.tokens.generate_response(user_id=user_id)


def verify_password(self, *, plain_password: str, hashed_password: str) -> bool:
    return self.pwd_context.verify(plain_password, hashed_password)

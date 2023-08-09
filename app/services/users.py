import os
import json
import secrets
import aiohttp
import typing as tp

from fastapi import HTTPException, UploadFile

from datetime import datetime, timedelta
from bson import ObjectId
from passlib.context import CryptContext

from app.config import settings
from app.repositories import UsersRepository
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def append_to_json_file(file_name, expire_date, _id, secure_number):
    try:
        with open(file_name, 'r') as file:
            data = dict(json.load(file))

        data[secure_number] = [expire_date, _id]
        with open(file_name, 'w') as file:
            json.dump(data, file)
    except FileNotFoundError:
        data_test = []
        with open(file_name, 'w') as file:
            json.dump(data_test, file)


async def read_secure_number(file_name, secure_number):
    # TODO refactor
    with open(file_name, 'r') as file:
        data = json.load(file)

    if secure_number not in data:
        raise HTTPException(status_code=409, detail='Invalid secure number.')

    expire_date, _id = data[secure_number]
    if datetime.now() > datetime.fromisoformat(expire_date):
        raise HTTPException(
            status_code=409, detail='Secure number has expired.')
    return _id


async def get_user_by_id(user_id: str) -> dict:
    return await UsersRepository().get_by_id(_id=ObjectId(user_id))  # type: ignore


async def save_user_avatar_image(user_id: str, body: UploadFile) -> tp.Dict[str, tp.Any]:
    try:
        user = await UsersRepository().get_by_id(ObjectId(user_id))
        if user and user.get('avatar_link'):
            file_path = user['avatar_link']
            if os.path.exists(file_path):
                os.remove(file_path)

        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        file_name = body.filename.replace(' ', '_')
        file_path = os.path.join("uploads", file_name)
        with open(file_path, "wb") as f:
            f.write(body.file.read())

        file_path = file_path.replace('\\', '/')

        await UsersRepository().update_by_id(ObjectId(user_id), {'avatar_link': file_path})

        image_link = f"{settings.SERVICE_URL}/{file_path}/"
        return {"avatar_link": image_link}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_user(user_id: str, instance: PatchUserUpdateRequest) -> tp.Dict[tp.Any, tp.Any] | None:
    data = instance.dict(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail='Bad request.')

    await UsersRepository().update_by_id(instance_id=ObjectId(user_id), instance=data)
    return await UsersRepository().get_by_id(_id=ObjectId(user_id))


async def get_all():
    return await UsersRepository().get_all()


async def create_user(person) -> dict:
    user = await UsersRepository().get_by_email(email=person.email)
    person.password = pwd_context.hash(person.password)
    if user:
        raise HTTPException(
            status_code=409, detail='User with such email already exists')
    return await UsersRepository().create(instance=person.dict())


async def login_user(data: LoginSchema) -> TokenSchema:
    user = await UsersRepository().get_by_email(email=data.email)
    if user is None:
        raise HTTPException(
            status_code=404, detail="No such user with chosen email.")

    if not pwd_context.verify(data.password, user.get('password')):
        raise HTTPException(status_code=401, detail='Incorrect credentials.')

    tokens = await services.create_tokens(user_id=str(user.get('_id')))
    return RetrieveLoginSchema(user=user, **tokens.dict())


async def check_exist_company_by_inn(tin: str) -> dict:
    """
    :param tin: Taxpayer Identification Number
    :return: True if there is an entry in the registry with this TIN, else return False
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api-fns.ru/api/egr?req={tin}&key={settings.API_FNS_KEY}') as response:
            # TODO: Fix the description
            if response.status == 403:
                raise HTTPException(
                    status_code=500,
                    detail='I\'ll fix the description later, if I threw it out, '
                           'then it means you can\'t make a request to the api-fns'
                )
            company_exist = await response.json()
            data = company_exist.get('items', None)
            if data is None or data == []:
                raise HTTPException(
                    status_code=404, detail='There no company with such TIN.')
            return data


async def collect_additional_info(additional_info: dict) -> dict:
    data = await check_exist_company_by_inn(tin=additional_info.get('inn', None))
    juridical_person = data[0]['ЮЛ']
    name = juridical_person['НаимСокрЮЛ']
    full_name = juridical_person['Руководитель']['ФИОПолн']
    address = juridical_person['Адрес']['АдресПолн']
    return {"name": name, "head": full_name, "address": address} | additional_info


async def forgot_password(email: EmailSchema):
    secure_number = secrets.randbelow(1000000)
    secure_number_str = f"{secure_number:06}"

    # TODO move to depends
    user = await UsersRepository().get_by_email(email=email.email)
    if user is None:
        raise HTTPException(
            status_code=404, detail='No such user with chosen email.')

    expire_date = datetime.now() + timedelta(minutes=30)
    await append_to_json_file(
        'reset_passwords.json',
        str(expire_date),
        str(user.get('_id')),
        secure_number_str
    )

    user_first_name = str(user.get('additional_info')['first_name'])
    await services.send_mail(
        email=email.email,
        content=f"{await services.open_html(str(user.get('email')), user_first_name, secure_number_str)}"
    )


async def reset_password(data: ResetPasswordsSchema):
    _id = await read_secure_number('reset_passwords.json', secure_number=data.secure_code)
    user = await get_user_by_id(user_id=_id)
    user['password'] = pwd_context.hash(data.password)
    await UsersRepository().update_by_id(ObjectId(_id), user)


async def activate_person(user_id: str):
    # TODO add fastapi Depends(404 status code will be returned)
    instance = await get_user_by_id(user_id=user_id)
    instance['is_verified'] = True
    await UsersRepository().update_by_id(instance_id=ObjectId(user_id), instance=instance)


async def delete_person(_id: str):
    instance = await get_user_by_id(user_id=_id)
    await UsersRepository().delete_by_id(_id=instance["_id"])


async def get_user_by_token(self, authorization: str) -> dict:
    user_id = await self.tokens.decode_access_jwt_token(authorization=authorization)
    return await self.get_user_by_id(user_id=user_id)


async def refresh_token(self, token: RefreshTokenSchema) -> TokenSchema:
    user_id = await self.tokens.decode_refresh_jwt_token(refresh_token=token.refresh_token)
    return await self.tokens.generate_response(user_id=user_id)


def verify_password(self, *, plain_password: str, hashed_password: str) -> bool:
    return self.pwd_context.verify(plain_password, hashed_password)

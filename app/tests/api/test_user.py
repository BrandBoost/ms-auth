import pytest
import mock
import jwt

from httpx import AsyncClient

from app.repositories import UsersRepository
from app.tests.data.user_factories import (
    UserFactoryLoginUnauthorized,
    LegalPersonCreateFactory,
    PrivatePersonCreateFactory
)
from app import services
from app.config import settings


class TestUsers:

    @pytest.mark.asyncio
    async def test_user_me(self, async_client, private_user_with_token):
        response = await async_client.get(
            url='/api/v1/users/me/',
            headers={
                 'Authorization': f'{settings.TOKEN_TYPE} {private_user_with_token["access_token"]}'
            }
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_user_me(self, async_client, private_user_with_token):
        response = await async_client.patch(
            url='/api/v1/users/me/',
            headers={
                 'Authorization': f'{settings.TOKEN_TYPE} {private_user_with_token["access_token"]}'
            },
            json={
                'additional_info': {
                    'some_info': 'asdasdasd'
                }
            }
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_user_me_invalid_token(self, async_client, private_user_with_token):
        response = await async_client.get(
            url='/api/v1/users/me/',
            headers={
                'Authorization': 'asdasdasdasdasd'
            }
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_register_private_person(self, async_client: AsyncClient, base_repository, global_dict):
        person_payload = PrivatePersonCreateFactory.build()
        response = await async_client.post('/api/v1/users/private_person/register/', json=person_payload.dict())
        # TODO move to docker-compose db
        payload = jwt.decode(response.json()["access_token"], settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload['id']

        global_dict["user_id"] = user_id
        global_dict["refresh_token"] = response.json()["refresh_token"]
        global_dict["email"] = person_payload.dict()["email"]
        global_dict["password"] = person_payload.dict()["password"]
        assert response.status_code == 201
        assert "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_register_legal_person(self, async_client: AsyncClient, base_repository):
        person_payload = LegalPersonCreateFactory.build()
        response = await async_client.post('/api/v1/users/legal_person/register/', json=person_payload.dict())
        payload = jwt.decode(response.json()["access_token"], settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload['id']

        assert response.status_code == 201
        assert "access_token" in response.json()

        await services.delete_person(user_id)

    @pytest.mark.asyncio
    async def test_login(self, async_client: AsyncClient, base_repository, global_dict):
        login_user = {
            "email": global_dict["email"],
            "password": global_dict["password"]
        }
        response = await async_client.post('/api/v1/users/login/', json=login_user)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_unauthorized_login(self, async_client: AsyncClient, base_repository):
        login_payload = UserFactoryLoginUnauthorized.build()
        response = await async_client.post('/api/v1/users/login/', json=login_payload.dict())

        assert response.status_code == 404
        assert response.json()['detail'] == 'No such user with chosen email.'

    @mock.patch('app.services.users.services.send_mail')
    @mock.patch('app.services.users.append_to_json_file')
    @pytest.mark.asyncio
    async def test_forgot_password(
            self,
            mock_append_to_json_file,
            mock_send_email,
            async_client: AsyncClient,
            base_repository,
            global_dict,
    ):
        user_data = {
            'email': 'some_mail@mail.ru',
            'additional_info': {
                'first_name': 'first_name',
                'last_name': 'last_name'
            }
        }
        user = await UsersRepository().create(user_data)
        person_payload = {'email': user_data['email']}
        mock_send_email.return_value = {}
        mock_append_to_json_file.return_value = {}
        response = await async_client.post('/api/v1/users/forgot_password/', json=person_payload)
        assert response.status_code == 200
        await UsersRepository().delete_by_id(str(user['_id']))

    @pytest.mark.asyncio
    async def test_forgot_password_invalid_email(self, async_client: AsyncClient, base_repository):
        person_payload = {
            "email": "test@gmail.com",
        }

        response = await async_client.post('/api/v1/users/forgot_password/', json=person_payload)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_refresh_token(self, async_client: AsyncClient, base_repository, global_dict):
        person_payload = {"refresh_token": global_dict["refresh_token"]}
        response = await async_client.post('/api/v1/users/refresh_token/', json=person_payload)

        assert response.status_code == 200

    # @pytest.mark.asyncio
    # async def test_refresh_token_unexpected(self, async_client: AsyncClient, base_repository):
    #     person_payload = {"refresh_token": "test"}
    #
    #     response = await async_client.post('/api/v1/users/refresh_token/', json=person_payload)
    #
    #     # TODO remove all tests with 500(if u know about errors they have to be handled)
    #     assert response.status_code == 500
    #     assert response.json()['detail'] == 'Unexpected Error occurred'

    # TODO
    @mock.patch('app.services.users.check_exist_company_by_inn')
    @pytest.mark.asyncio
    async def test_inn(self, exist_company, async_client: AsyncClient, base_repository):
        inn_id = settings.USER_INN
        exist_company.return_value = None
        response = await async_client.post(f'/api/v1/users/check_inn/?inn={inn_id}')

        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_activate(self, async_client: AsyncClient, base_repository, global_dict):
        response = await async_client.post(f'/api/v1/users/activate/{global_dict["user_id"]}/')
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_user(self, async_client: AsyncClient, base_repository, global_dict):
        await services.delete_person(global_dict["user_id"])

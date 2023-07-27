import pytest
from httpx import AsyncClient

from app.config import settings
from app.tests.configtest import async_client, event_loop, base_repository, mongo_client, global_dict, \
    private_user_with_token
from app.tests.data.projects_factories import ProjectCreateFactory, ProjectUpdateFactory


@pytest.mark.asyncio
async def test_create_project(async_client: AsyncClient, base_repository, global_dict, private_user_with_token):
    project_payload = ProjectCreateFactory.build()
    response = await async_client.post(
        '/api/v1/projects/create/',
        json=project_payload.dict(),
        headers={
            'Authorization': f'{settings.TOKEN_TYPE} {private_user_with_token["access_token"]}'
        }, )
    global_dict["project_id"] = response.json()["_id"]
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_projects(async_client, private_user_with_token):
    response = await async_client.get(
        url=f'/api/v1/projects/get_projects/',
        headers={
            'Authorization': f'{settings.TOKEN_TYPE} {private_user_with_token["access_token"]}'
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_project_by_id(async_client, private_user_with_token, global_dict):
    response = await async_client.get(
        url=f'/api/v1/projects/get_project_by_id/{global_dict["project_id"]}/',
        headers={
            'Authorization': f'{settings.TOKEN_TYPE} {private_user_with_token["access_token"]}'
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_project_members(async_client, private_user_with_token, global_dict):
    response = await async_client.get(
        url=f'/api/v1/projects/get_project_by_id/{global_dict["project_id"]}/',
        headers={
            'Authorization': f'{settings.TOKEN_TYPE} {private_user_with_token["access_token"]}'
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_project(async_client, private_user_with_token, global_dict):
    project_payload = ProjectUpdateFactory.build()
    response = await async_client.patch(
        json=project_payload.dict(),
        url=f'/api/v1/projects/update_project/{global_dict["project_id"]}/',
        headers={
            'Authorization': f'{settings.TOKEN_TYPE} {private_user_with_token["access_token"]}'
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_project_by_id(async_client, private_user_with_token, global_dict):
    response = await async_client.delete(
        url=f'/api/v1/projects/delete_project_by_id/{global_dict["project_id"]}/',
        headers={
            'Authorization': f'{settings.TOKEN_TYPE} {private_user_with_token["access_token"]}'
        },
    )
    assert response.status_code == 200

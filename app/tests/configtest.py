<<<<<<< HEAD
import asyncio
import mongomock
import pytest

from typing import Generator, AsyncGenerator
=======
import mongomock
import pytest

from asyncio import get_event_loop

>>>>>>> develop

import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime
from app.main import app

from app.repositories import UsersRepository
from app.services import create_token

from app.tests.data.user_factories import (
    UserFactoryLoginUnauthorized,
    LegalPersonCreateFactory,
    PrivatePersonCreateFactory
)
from app.repositories import UsersRepository


@pytest_asyncio.fixture()
async def private_user_with_token():
    person_payload = PrivatePersonCreateFactory.build()
    person_payload = person_payload.dict()
    person_payload.update({'is_verified': True, 'role': 'legal person', 'created_at': datetime.now()})
    user_data = await UsersRepository().create(person_payload)
    access_token = await create_token(token_type='access', user_id=str(user_data['_id']))
    user_data['access_token'] = access_token
    return user_data


@pytest_asyncio.fixture(scope="session")
<<<<<<< HEAD
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
def async_client():
    from app.main import app
    import httpx

    return httpx.AsyncClient(app=app, base_url='http://test')
=======
def event_loop():
    loop = get_event_loop()
    yield loop


@pytest_asyncio.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
>>>>>>> develop


@pytest_asyncio.fixture
def mongo_client():
    return None
    return mongomock.MongoClient()


@pytest_asyncio.fixture
async def base_repository(mongo_client):
    return None
    db = mongo_client['testdb']
    collection = db['test']
    repository = UsersRepository()
    repository.collection = collection
    return repository


<<<<<<< HEAD
@pytest_asyncio.fixture(scope="class")
=======
@pytest_asyncio.fixture(scope="session")
>>>>>>> develop
def global_dict():
    return {}


pytestmark = pytest.mark.asyncio

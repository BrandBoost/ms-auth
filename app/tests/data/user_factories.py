import faker

from datetime import datetime
from typing import List

from app.config import settings

from factory import Factory, Faker, SubFactory

from app.schemas.projects import BaseProjectCreateUpdate, ProjectCreate
from app.schemas.users import Login, BaseUserCreate

fake = faker.Faker()


class UserFactoryLoginUnauthorized(Factory):
    class Meta:
        model = Login

    email = Faker("email")
    password = Faker("password")


class PrivatePersonAdditionalFactory(Factory):
    class Meta:
        model = dict

    first_name = Faker("first_name")
    last_name = Faker("last_name")


class LegalPersonAdditionalFactory(PrivatePersonAdditionalFactory):
    class Meta:
        model = dict

    inn = settings.USER_INN
    company_name = Faker("name")


class UserCreateFactory(Factory):
    class Meta:
        model = dict

    email = Faker("email")
    phone = fake.phone_number()
    password = Faker("password")


class LegalPersonCreateFactory(UserCreateFactory):
    class Meta:
        model = BaseUserCreate

    additional_info = SubFactory(LegalPersonAdditionalFactory)


class PrivatePersonCreateFactory(UserCreateFactory):
    class Meta:
        model = BaseUserCreate

    additional_info = SubFactory(PrivatePersonAdditionalFactory)

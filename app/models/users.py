import typing as tp

from datetime import datetime
from typing import Dict, Union, Type

from beanie import Document

from app.enums.users import UserRole


class PrivatePerson:
    first_name: str
    last_name: str


class LegalPerson:
    name: str
    inn: str
    address: str
    bank_details: str
    head: str


class BaseUser(Document):
    _id: str
    email: str
    phone: str
    code: int
    password: str
    new_password: str
    created_at: datetime
    is_verified: bool
    role: UserRole
    additional_info: tp.Dict[Union[LegalPerson, PrivatePerson], tp.Any] = Dict[  # type: ignore
        Union[Type[LegalPerson], Type[PrivatePerson]], Type[None]
    ]

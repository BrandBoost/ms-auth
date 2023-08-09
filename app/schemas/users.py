from datetime import datetime
from typing import Union, Any, Optional, List

from fastapi.exceptions import HTTPException

from bson import ObjectId
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, validator, Field, ValidationError, root_validator

from app.config import settings
from app.enums import UserRole
from app.schemas.mongo_validators import PyObjectId
from app.schemas.tokens import Token


class UploadAvatarResponse(BaseModel):
    avatar_link: str


class PrivatePersonBase(BaseModel):
    first_name: str
    last_name: str


class PrivatePersonCreateUpdate(PrivatePersonBase):
    ...


class PrivatePersonRead(PrivatePersonBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str
    phone: str
    created_at: datetime
    is_verified: bool


class LegalPersonBaseCreate(PrivatePersonBase):
    inn: str
    company_name: str


class LegalPersonBase(LegalPersonBaseCreate):
    address: Optional[str]
    bank_details: Optional[str]


class LegalPersonCreateUpdate(LegalPersonBase):
    ...


class LegalPersonRead(LegalPersonBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str
    password: str
    phone: str
    created_at: datetime
    is_verified: bool


class BaseUserCreateUpdate(BaseModel):
    email: str
    phone: str
    password: str
    created_at: datetime
    is_verified: bool
    role: UserRole
    additional_info: Union[PrivatePersonCreateUpdate, LegalPersonCreateUpdate]


class BaseUserUpdatePassword(BaseModel):
    email: str
    new_password: Optional[str] = None
    code: Optional[int] = None


class BaseUserRead(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str
    phone: str
    created_at: datetime
    is_verified: bool
    role: UserRole
    additional_info: dict
    avatar_link: str | None

    @root_validator()
    def validator(cls, values: dict) -> dict:
        values['avatar_link'] = f"{settings.SERVICE_URL}/{values['avatar_link']}/"
        return values

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PatchUserUpdateRequest(BaseModel):
    email: Optional[str]
    phone: Optional[str]
    additional_info: Optional[dict]

    @validator('email')
    def validate_email(cls, email: str) -> str:
        try:
            validate_email(email)
            return email
        except EmailNotValidError:
            raise ValueError('Invalid email')


class UserCreateUpdate(BaseUserCreateUpdate):
    role: UserRole = UserRole.ADMIN


class UserRead(BaseUserRead):
    role: UserRole = UserRole.ADMIN


class LegalUserCreateUpdate(BaseUserCreateUpdate):
    additional_info: LegalPersonCreateUpdate
    role: UserRole = UserRole.LEGAL_PERSON


class LegalUserRead(BaseUserRead):
    role: UserRole = UserRole.LEGAL_PERSON


class PrivateUserCreateUpdate(BaseUserCreateUpdate):
    additional_info: PrivatePersonCreateUpdate
    role: UserRole = UserRole.PRIVATE_PERSON


class BaseUserCreate(BaseModel):
    email: str
    phone: str
    password: str
    additional_info: Any


class LegalUserCreate(BaseUserCreate):
    additional_info: LegalPersonBaseCreate


class PrivateUserCreate(BaseUserCreate):
    additional_info: PrivatePersonCreateUpdate


class PrivateUserRead(BaseUserRead):
    role: UserRole = UserRole.PRIVATE_PERSON


class Login(BaseModel):
    email: str
    password: str


class RetrieveLogin(Token):
    user: BaseUserRead

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Email(BaseModel):
    email: str


class ResetPasswords(BaseModel):
    secure_code: str
    password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        if "password" in values and confirm_password != values["password"]:
            raise HTTPException(status_code=401, detail="Passwords do not match")
        return confirm_password

    def validate_passwords(self):
        try:
            self.dict()
        except ValidationError as e:
            raise ValueError(str(e)) from e


class ReadUserProjects(BaseModel):
    projects: List[str]

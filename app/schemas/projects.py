from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from pydantic import BaseModel, Field

from app.schemas.mongo_validators import PyObjectId


class BaseProjectCreateUpdate(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    owner: str
    created_at: datetime
    members: List[str]
    sites: List[str]
    activity_types: List[str]
    country: str
    region: str
    social_networks: List[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class BaseProjectRead(BaseProjectCreateUpdate):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")


class ProjectReadMembers(BaseModel):
    members: List[str]


class PatchProjectUpdateRequest(BaseModel):
    name: Optional[str]
    country: Optional[str]
    region: Optional[str]
    members: Optional[list]
    sites: Optional[list]
    activity_types: Optional[list]
    social_networks: Optional[list]


class ProjectCreate(BaseModel):
    name: str
    members: List[str]
    sites: List[str]
    activity_types: List[str]
    country: str
    region: str
    social_networks: List[str]

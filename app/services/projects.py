from fastapi import HTTPException
from bson import ObjectId

from app.repositories.projects import ProjectsRepository
from app.schemas.projects import PatchProjectUpdateRequest


async def get_project_by_id(project_id: str, owner_id: str) -> dict:
    return await ProjectsRepository().get_project_by_id(_id=ObjectId(project_id), owner_id=owner_id)  # type: ignore


async def update_project(project_id: str, instance: PatchProjectUpdateRequest, owner_id: str):
    data = instance.dict(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail='Bad request.')

    await ProjectsRepository().update_by_id(instance_id=ObjectId(project_id), instance=data)
    return await ProjectsRepository().get_project_by_id(_id=ObjectId(project_id), owner_id=owner_id)


async def get_all_projects(owner_id: str):
    return await ProjectsRepository().get_all_projects(owner_id=owner_id)


async def create_project(project, owner_id: str) -> dict:
    user = await ProjectsRepository().get_by_name(name=project.name)
    if user:
        raise HTTPException(status_code=409, detail='User with such name already exists')
    return await ProjectsRepository().create_project(instance=project.dict(), owner_id=owner_id)


async def delete_project_by_id(project_id: str, owner_id: str):
    return await ProjectsRepository().delete_project_by_id(_id=project_id, owner_id=owner_id)


async def add_user(project_id: str, user_id: str):
    user = await ProjectsRepository().get_user_in_members(user_id=user_id, _id=project_id)
    if user:
        raise HTTPException(status_code=409, detail="Such user already exist")
    return await ProjectsRepository().add_user_to_project(user_id=user_id, _id=project_id)


async def delete_user(project_id: str, user_id: str):
    user = await ProjectsRepository().get_user_in_members(user_id=user_id, _id=project_id)
    if not user:
        raise HTTPException(status_code=409, detail="Such user doesn't exist")
    return await ProjectsRepository().delete_user_from_project(user_id=user_id, _id=project_id)

import typing as tp

from datetime import datetime

from fastapi import APIRouter, Request

from app.schemas.projects import (
    BaseProjectCreateUpdate,
    BaseProjectRead,
    ProjectCreate,
    PatchProjectUpdateRequest,
    ProjectReadMembers
)
from fastapi.responses import PlainTextResponse
from app.services import projects


project_routes = APIRouter()


@project_routes.post("/create/", status_code=201, response_model=BaseProjectRead)
async def register_private_person(request: Request, data: ProjectCreate) -> tp.Dict[str, tp.Any]:
    user_id = request.state.user_id
    project = BaseProjectCreateUpdate(
        owner=user_id,
        created_at=datetime.now(), **data.dict()
    )
    user = await projects.create_project(project=project)
    return user


@project_routes.get("/get_projects/", status_code=200, response_model=tp.List[BaseProjectCreateUpdate])
async def get_project(request: Request):
    user_id = request.state.user_id
    return await projects.get_all_projects(owner_id=user_id)


@project_routes.get("/get/{project_id}/",
                    status_code=200,
                    response_model=BaseProjectCreateUpdate)
async def get_project_by_id(request: Request, project_id: str):
    user_id = request.state.user_id
    return await projects.get_project_by_id(project_id=project_id, owner_id=user_id)


@project_routes.get("/get_project_members/{project_id}/",
                    status_code=200,
                    response_model=ProjectReadMembers)
async def get_project_members(request: Request, project_id: str):
    user_id = request.state.user_id
    return await projects.get_project_by_id(project_id=project_id, owner_id=user_id)


@project_routes.patch("/patch/{project_id}/", status_code=200, response_model=BaseProjectCreateUpdate)
async def update_user_me(request: Request, body: PatchProjectUpdateRequest, project_id: str):
    user_id = request.state.user_id
    return await projects.update_project(project_id=project_id, instance=body, owner_id=user_id)


@project_routes.delete("/delete/{project_id}/", status_code=204)
async def delete_user_parser_by_id(request: Request, project_id: str,):
    user_id = request.state.user_id
    await projects.delete_project_by_id(project_id=project_id, owner_id=user_id)
    return PlainTextResponse("Deletion completed successfully")

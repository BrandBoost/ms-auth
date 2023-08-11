import typing as tp
import os

from fastapi import APIRouter, Request, UploadFile, HTTPException
from fastapi.responses import FileResponse

from app import services
from app.schemas.users import UploadAvatarResponse

media = APIRouter()


@media.patch(
    "/me/avatar/",
    status_code=200,
    response_model=UploadAvatarResponse
)
async def upload_avatar(request: Request, file: UploadFile) -> tp.Dict[str, tp.Any]:
    return await services.save_user_avatar_image(user_id=request.state.user_id, file=file)


@media.get('/userdata/avatars/{file_name}/')
async def get_media(file_name: str):

    file_path = os.path.join("media/userdata/avatars", file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=404, detail="File not found")

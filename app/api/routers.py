from fastapi import APIRouter

from app.api.v1.users import user_routes
<<<<<<< HEAD
=======
from app.api.v1.projects import project_routes
>>>>>>> develop

# users_router = UserRouter()

v1_router = APIRouter(prefix='/api/v1')

<<<<<<< HEAD
v1_router.include_router(user_routes, prefix='/users', tags=['auth'])
# v1_router.include_router(users_router.api_router, prefix="/users", tags=["auth"])
=======
v1_router.include_router(user_routes, prefix='/users', tags=['users_auth'])
# v1_router.include_router(users_router.api_router, prefix="/users", tags=["auth"])
v1_router.include_router(project_routes, prefix='/projects', tags=['projects'])
>>>>>>> develop

from app.repositories import BaseRepository
import typing as tp

from bson import ObjectId


class UsersRepository(BaseRepository):
    def __init__(self):
        self.collection = 'users'
        super().__init__()

    async def add_project_to_user(self, _id: tp.Union[str, ObjectId], project_id: str):
        user_id = ObjectId(_id) if isinstance(_id, str) else _id
        await self.db[self.collection].update_one(
            {"_id": user_id},
            {"$addToSet": {"projects": project_id}}
        )
        await self.db[self.collection].find_one({"_id": user_id})

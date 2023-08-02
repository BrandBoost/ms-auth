from app.repositories import BaseRepository
import typing as tp

from bson import ObjectId

from app.schemas import BaseUserRead


class ProjectsRepository(BaseRepository):
    def __init__(self):
        self.collection = 'projects'
        super().__init__()

    async def delete_project_by_id(self, _id: tp.Union[str, ObjectId], owner_id: str) -> None:
        project_id = ObjectId(_id) if isinstance(_id, str) else _id
        await self.db[self.collection].delete_one({'_id': project_id, "owner": owner_id})

    async def get_project_by_id(self, _id: ObjectId, owner_id: str):
        return await self.db[self.collection].find_one({"_id": _id, "owner": owner_id})

    async def get_user_in_members(self, user_id: str, _id: tp.Union[str, ObjectId]):
        project_id = ObjectId(_id) if isinstance(_id, str) else _id
        return await self.db[self.collection].find_one({"_id": project_id, "members": user_id})

    async def get_all_projects(self, owner_id: str) -> tp.List[BaseUserRead]:
        await self.get_db()
        return await self.db[self.collection].find({"owner": owner_id}).to_list(length=None)

    async def add_user_to_project(self, user_id: str, _id: tp.Union[str, ObjectId], owner_id: str):
        project_id = ObjectId(_id) if isinstance(_id, str) else _id
        await self.db[self.collection].update_one(
            {"_id": project_id, "owner": owner_id},
            {"$addToSet": {"members": user_id}}
        )
        return await self.db[self.collection].find_one({"_id": project_id})

    async def delete_user_from_project(self, user_id: str, _id: tp.Union[str, ObjectId], owner_id: str):
        project_id = ObjectId(_id) if isinstance(_id, str) else _id
        await self.db[self.collection].update_one(
            {"_id": project_id, "owner": owner_id},
            {"$pull": {"members": user_id}},

        )
        return await self.db[self.collection].find_one({"_id": project_id})

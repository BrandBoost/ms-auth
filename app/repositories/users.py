from bson import ObjectId

from app.repositories import BaseRepository
from app.config import settings


class UsersRepository(BaseRepository):
    def __init__(self):
        self.collection = "users"
        super().__init__()

    async def delete_user_parsers(self, owner_id: ObjectId):
        return await self.db[settings.PARSER_COLLECTION_NAME].delete_many({"owner_id": owner_id})  # type: ignore

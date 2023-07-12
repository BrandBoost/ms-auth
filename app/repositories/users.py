from app.repositories import BaseRepository


class UsersRepository(BaseRepository):
    def __init__(self):
        self.collection = 'users'
        super().__init__()

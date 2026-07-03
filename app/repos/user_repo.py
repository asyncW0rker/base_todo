from app.models import User
from app.repos.base_repo import BaseRepository


class UserRepository(BaseRepository):
    model = User

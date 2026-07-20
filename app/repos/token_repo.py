from app.database.models import Token
from app.repos.base_repo import BaseRepository


class TokenRepository(BaseRepository):
    model = Token

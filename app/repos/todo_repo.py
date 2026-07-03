from app.database.models import ToDo
from app.repos.base_repo import BaseRepository


class ToDoRepository(BaseRepository):
    model = ToDo

from app.database.models import ImportJob
from app.repos.base_repo import BaseRepository


class ImportJobRepository(BaseRepository):
    model = ImportJob

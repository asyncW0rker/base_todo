from app.database.models import ExportJob
from app.repos.base_repo import BaseRepository


class ExportJobRepository(BaseRepository):
    model = ExportJob

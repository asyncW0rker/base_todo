from app.database.models import AnalyticsJob
from app.repos.base_repo import BaseRepository


class AnalyticsJobRepository(BaseRepository):
    model = AnalyticsJob

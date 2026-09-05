from app.database.models import AuditLog
from app.repos.base_repo import BaseRepository


class AuditLogRepository(BaseRepository):
    model = AuditLog

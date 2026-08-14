from app.database.models import Attachment
from app.repos.base_repo import BaseRepository


class AttachmentRepository(BaseRepository):
    model = Attachment

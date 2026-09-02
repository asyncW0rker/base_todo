from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ToDo
from app.database.schemas import ToDoCreate, ToDoUpdate, ToDoFilterParams, \
    ToDoStatusUpdate, UserRole, ToDoPatch, ToDoSearchParams, ToDoWithUploads, BaseOrderingParams
from app.errors.http_exceptions import HTTPUserNotFoundException, HTTPToDoNotFoundException, \
    HTTPToDoVersionMismatchException
from app.repos.attachment_repo import AttachmentRepository
from app.repos.todo_repo import ToDoRepository
from app.repos.user_repo import UserRepository
from app.utils.s3_manager import S3Manager, get_s3_manager


@dataclass
class ToDoService:
    todo_repo: ToDoRepository = ToDoRepository()
    user_repo: UserRepository = UserRepository()
    s3_manager: S3Manager = field(default_factory=get_s3_manager)
    attachment_repo: AttachmentRepository = AttachmentRepository()

    async def _check_user_existence(self, session: AsyncSession, user_id: int) -> None:
        user = await self.user_repo.get_one(session, user_id)
        if user is None:
            raise HTTPUserNotFoundException

    @staticmethod
    def _get_filter_params_from_user_data(user_data: dict[str, Any]) -> dict[str, Any]:
        user_role, user_id = user_data.get("role"), user_data.get("sub")
        filter_params = {"user_id": int(user_id)} if user_role == UserRole.USER else {}
        return filter_params

    async def create_todo(self, session: AsyncSession, creation_data: ToDoCreate) -> ToDoWithUploads:
        if creation_data.user_id is not None:
            await self._check_user_existence(session, creation_data.user_id)

        creation_params = creation_data.model_dump()
        attachments_meta = creation_params.pop("attachments_meta", [])
        upload_urls = []
        attachments_data = []

        todo = await self.todo_repo.create_one_uncommited(session, creation_params)

        for attachment in attachments_meta:
            storage_key = self.s3_manager.generate_file_key(todo.id, attachment["filename"])
            upload_url = await self.s3_manager.generate_presigned_upload_url(storage_key, attachment["content_type"])
            upload_urls.append({
                "storage_key": storage_key,
                "upload_url": upload_url
            })
            attachments_data.append({
                **attachment,
                "storage_key": storage_key,
                "todo_id": todo.id,
            })

        await self.attachment_repo.create_many(session, attachments_data)

        return ToDoWithUploads(
            todo=todo,
            upload_urls=upload_urls,
        )

    async def get_todo(self, session: AsyncSession, todo_id: int, current_user_info: dict[str, Any]) -> ToDo | None:
        todo = await self.todo_repo.get_one(session, todo_id)
        if todo is None:
            raise HTTPToDoNotFoundException

        if current_user_info.get("role") == UserRole.USER and todo.user_id != int(current_user_info.get("sub")):
            raise HTTPToDoNotFoundException

        return todo

    async def get_all_todos(self, session: AsyncSession):
        return await self.todo_repo.get_all(session)

    async def get_many_todos(
        self,
        session: AsyncSession,
        ordering_params: BaseOrderingParams,
        filter_params: ToDoFilterParams,
        search_params: ToDoSearchParams | None,
        current_user_info: dict[str, Any],
    ):
        filter_params_dict = filter_params.model_dump()
        user_filter_params = self._get_filter_params_from_user_data(current_user_info)
        filter_params_dict.update(user_filter_params)
        return await self.todo_repo.get_many(
            session=session,
            ordering_params=ordering_params.model_dump(),
            filter_params=filter_params_dict,
            search_params=search_params.model_dump() if search_params else {},
        )

    async def update_todo(
        self,
        session: AsyncSession,
        todo_id: int, update_data: ToDoUpdate | ToDoPatch,
        current_user_info: dict[str, Any],
    ):
        if update_data.user_id is not None:
            await self._check_user_existence(session, update_data.user_id)

        filter_params = self._get_filter_params_from_user_data(current_user_info)
        filter_params["version"] = update_data.version
        update_data.version += 1

        changed_todo = await self.todo_repo.update_one(
            session=session, item_id=todo_id, filter_params=filter_params, update_data=update_data.model_dump()
        )

        if changed_todo is None:
            todo = await self.get_todo(session, todo_id, current_user_info)
            raise HTTPToDoVersionMismatchException(detail=f"Actual version for ToDo is {todo.version}")

        return changed_todo

    async def update_status_for_todos(
        self, session: AsyncSession, update_data: ToDoStatusUpdate, current_user_info: dict[str, Any],
    ):
        update_data_dict = update_data.model_dump()
        todos_ids = update_data_dict.pop("ids")
        filter_params = self._get_filter_params_from_user_data(current_user_info)

        changed_todos_count = await self.todo_repo.update_many(
            session=session, items_ids=todos_ids, filter_params=filter_params, update_data=update_data_dict
        )
        return {
            "message": f"Updated_count: {changed_todos_count}"
        }

    async def delete_todo(self, session: AsyncSession, todo_id: int):
        deleted_todos_count = await self.todo_repo.delete_one(session, todo_id)
        if deleted_todos_count == 0:
            raise HTTPToDoNotFoundException
        return {"message": "ToDo deleted"}

    async def delete_all_todos(self, session: AsyncSession):
        await self.todo_repo.delete_all(session)
        return {"message": "All todos deleted"}


@lru_cache
def get_todo_service() -> ToDoService:
    return ToDoService()

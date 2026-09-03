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
from app.utils.rbac import ownership_and_role_access_to_object, filter_data_by_user_id_and_role
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

    async def create_todo(self, session: AsyncSession, creation_data: ToDoCreate) -> ToDoWithUploads:
        if creation_data.user_id is not None:
            await self._check_user_existence(session, creation_data.user_id)

        creation_params = creation_data.model_dump()
        attachments_meta = creation_params.pop("attachments_meta", [])
        upload_urls = []
        attachments_data = []

        todo = await self.todo_repo.create_one_uncommited(session, creation_params)

        for attachment in attachments_meta:
            storage_key = self.s3_manager.generate_file_key_for_attachments(todo.id, attachment["filename"])
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

    @ownership_and_role_access_to_object(UserRole.MANAGER)
    async def get_todo(self, session: AsyncSession, todo_id: int, current_user_info: dict[str, Any]) -> ToDo | None:
        todo = await self.todo_repo.get_one(session, todo_id)
        if todo is None:
            raise HTTPToDoNotFoundException
        return todo

    async def get_all_todos(self, session: AsyncSession):
        return await self.todo_repo.get_all(session)

    @filter_data_by_user_id_and_role(UserRole.MANAGER)
    async def get_many_todos(
        self,
        session: AsyncSession,
        ordering_params: BaseOrderingParams,
        filter_params: ToDoFilterParams | dict,
        search_params: ToDoSearchParams | None,
        current_user_info: dict[str, Any],
    ):
        return await self.todo_repo.get_many(
            session=session,
            ordering_params=ordering_params.model_dump(),
            filter_params=filter_params,
            search_params=search_params.model_dump() if search_params else {},
        )

    @filter_data_by_user_id_and_role(UserRole.MANAGER)
    async def update_todo(
        self,
        session: AsyncSession,
        todo_id: int,
        update_data: ToDoUpdate | ToDoPatch,
        current_user_info: dict[str, Any],
        filter_params: Any | None = None,
    ):
        if update_data.user_id is not None:
            await self._check_user_existence(session, update_data.user_id)

        filter_params = filter_params or {}
        filter_params["version"] = update_data.version
        update_data.version += 1

        changed_todo = await self.todo_repo.update_one(
            session=session, item_id=todo_id, filter_params=filter_params, update_data=update_data.model_dump()
        )

        if changed_todo is None:
            todo = await self.get_todo(session=session, todo_id=todo_id, current_user_info=current_user_info)
            raise HTTPToDoVersionMismatchException(detail=f"Actual version for ToDo is {todo.version}")

        return changed_todo

    @filter_data_by_user_id_and_role(UserRole.MANAGER)
    async def update_status_for_todos(
        self,
        session: AsyncSession,
        update_data: ToDoStatusUpdate,
        current_user_info: dict[str, Any],
        filter_params: Any | None = None,
    ):
        filter_params = filter_params or {}
        update_data_dict = update_data.model_dump()
        todos_ids = update_data_dict.pop("ids")

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

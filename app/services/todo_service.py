from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ToDo
from app.database.schemas import ToDoCreate, ToDoUpdate, ToDoFilterParams, ToDoOrderingParams, \
    ToDoAnalyticsFilterParams, ToDoAnalyticsOutput, ToDoStatusUpdate, UserRole, ToDoPatch
from app.errors.exceptions import TimezoneException, HTTPUserNotFoundException, HTTPToDoNotFoundException, \
    HTTPInvalidTimezoneException, HTTPToDoVersionMismatchException
from app.repos.todo_repo import ToDoRepository
from app.repos.user_repo import UserRepository


@dataclass
class ToDoService:
    repo: ToDoRepository = ToDoRepository()
    user_repo: UserRepository = UserRepository()

    async def _check_user_existence(self, session: AsyncSession, user_id: int) -> None:
        user = await self.user_repo.get_one(session, user_id)
        if user is None:
            raise HTTPUserNotFoundException

    @staticmethod
    def _get_filter_params_from_user_data(user_data: dict[str, Any]) -> dict[str, Any]:
        user_role, user_id = user_data.get("role"), user_data.get("sub")
        filter_params = {"user_id": int(user_id)} if user_role == UserRole.USER else {}
        return filter_params

    async def create_todo(self, session: AsyncSession, creation_data: ToDoCreate) -> ToDo:
        if creation_data.user_id is not None:
            await self._check_user_existence(session, creation_data.user_id)

        return await self.repo.create_one(session, creation_data.model_dump())

    async def get_todo(self, session: AsyncSession, todo_id: int, current_user_info: dict[str, Any]) -> ToDo | None:
        todo = await self.repo.get_one(session, todo_id)
        if todo is None:
            raise HTTPToDoNotFoundException

        if current_user_info.get("role") == UserRole.USER and todo.user_id != int(current_user_info.get("sub")):
            raise HTTPToDoNotFoundException

        return todo

    async def get_all_todos(self, session: AsyncSession):
        return await self.repo.get_all(session)

    async def get_many_todos(
        self,
        session: AsyncSession,
        ordering_params: ToDoOrderingParams,
        filter_params: ToDoFilterParams,
        current_user_info: dict[str, Any],
    ):
        filter_params_dict = filter_params.model_dump()
        if current_user_info.get("role") == UserRole.USER:
            filter_params_dict["user_id"] = int(current_user_info.get("sub"))

        return await self.repo.get_many(
            session=session,
            ordering_params=ordering_params.model_dump(),
            filter_params=filter_params_dict,
        )

    async def get_analytics(
            self, session: AsyncSession, filter_params: ToDoAnalyticsFilterParams
    ) -> ToDoAnalyticsOutput:
        try:
            analytics = await self.repo.get_analytics(session, filter_params.timezone)
            return ToDoAnalyticsOutput.model_validate(analytics)
        except TimezoneException:
            raise HTTPInvalidTimezoneException

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

        changed_todo = await self.repo.update_one(
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

        changed_todos_count = await self.repo.update_many(
            session=session, items_ids=todos_ids, filter_params=filter_params, update_data=update_data_dict
        )
        return {
            "updated_count": changed_todos_count
        }

    async def delete_todo(self, session: AsyncSession, todo_id: int):
        deleted_todos_count = await self.repo.delete_one(session, todo_id)
        if deleted_todos_count == 0:
            raise HTTPToDoNotFoundException
        return {"message": "ToDo deleted"}

    async def delete_all_todos(self, session: AsyncSession):
        await self.repo.delete_all(session)
        return {"message": "All todos deleted"}


@lru_cache
def get_todo_service() -> ToDoService:
    return ToDoService()

import functools
from typing import Any, Awaitable

from fastapi import Depends, Path

from app.database.schemas import UserRole
from app.errors.http_exceptions import HTTPRolePermissionDeniedException, HTTPPrivatePermissionDeniedException
from app.services.auth_service import AuthService, get_auth_service
from app.utils.security import get_token
from app.utils.utils import get_current_user_payload


class RBACServiceMixin:
    @staticmethod
    def _check_user_permission(
            allowed_user_id: int,
            current_user_info: dict[str, Any],
    ):
        user_id, user_role = int(current_user_info.get("sub")), current_user_info.get("role")
        if user_role == UserRole.USER and user_id != allowed_user_id:
            raise HTTPPrivatePermissionDeniedException


def check_ownership_and_role_access(minimum_role: UserRole = UserRole.ADMIN):
    def wrapper(service_action: Awaitable | callable):
        @functools.wraps(service_action)
        async def inner(*args, current_user_info, **kwargs):
            data = await service_action(*args, **kwargs, current_user_info=current_user_info)
            user_id, user_role = int(current_user_info.get("sub")), current_user_info.get("role")
            if data.user_id != user_id and user_role not in [UserRole.ADMIN, minimum_role]:
                raise HTTPPrivatePermissionDeniedException
            return data
        return inner

    return wrapper


def filter_data_by_user_id_and_role(minimum_role: UserRole = UserRole.ADMIN):
    def wrapper(service_action: Awaitable | callable):
        @functools.wraps(service_action)
        async def inner(*args, current_user_info, **kwargs):
            filter_params = kwargs["filter_params"].model_dump() if kwargs.get("filter_params") else {}
            user_id, user_role = int(current_user_info.get("sub")), current_user_info.get("role")
            available_roles = [UserRole.ADMIN, minimum_role]
            user_params = {"user_id": int(user_id)} if user_role not in available_roles else {}
            filter_params.update(user_params)
            kwargs["filter_params"] = filter_params
            return await service_action(*args, **kwargs, current_user_info=current_user_info)
        return inner
    return wrapper


def check_role_permission_dep(required_role: UserRole = UserRole.ADMIN):
    def check_permission(
        token: str = Depends(get_token),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        payload = auth_service.decode_access_token(token)
        user_role = payload.get("role")
        if user_role not in [required_role, UserRole.ADMIN]:
            raise HTTPRolePermissionDeniedException

    return check_permission


def check_private_user_permission_dep(
    user_id: int = Path(...),
    user_payload: dict[str, Any] = Depends(get_current_user_payload),
):
    user_id_from_token = int(user_payload.get("sub"))
    user_role = user_payload.get("role")
    if user_id != user_id_from_token and user_role != UserRole.ADMIN:
        raise HTTPPrivatePermissionDeniedException

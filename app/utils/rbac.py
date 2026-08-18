from typing import Any

from fastapi import Depends, Path

from app.database.schemas import UserRole
from app.errors.exceptions import HTTPRolePermissionDeniedException, HTTPPrivatePermissionDeniedException
from app.services.auth_service import AuthService, get_auth_service
from app.utils.security import get_token
from app.utils.utils import get_current_user_payload


def role_permission_required(required_role: UserRole = UserRole.ADMIN):
    def check_permission(
        token: str = Depends(get_token),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        payload = auth_service.decode_access_token(token)
        user_role = payload.get("role")
        if user_role not in [required_role, UserRole.ADMIN]:
            raise HTTPRolePermissionDeniedException

    return check_permission


def private_user_permission_required(
    user_id: int = Path(...),
    user_payload: dict[str, Any] = Depends(get_current_user_payload),
):
    user_id_from_token = int(user_payload.get("sub"))
    user_role = user_payload.get("role")
    if user_id != user_id_from_token and user_role != UserRole.ADMIN:
        raise HTTPPrivatePermissionDeniedException

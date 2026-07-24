from fastapi import Depends

from app.database.schemas import UserRole
from app.errors.exceptions import HTTPRolePermissionDeniedException
from app.services.auth_service import AuthService, get_auth_service
from app.utils.security import JWTManager, oauth_scheme


def admin_permission_required(token: str = Depends(oauth_scheme), jwt_manager: JWTManager=Depends()):
    pass


def role_permission_required(required_role: UserRole = UserRole.ADMIN):
    def check_permission(
        token: str = Depends(oauth_scheme),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        payload = auth_service.decode_access_token(token)
        if payload['role'] not in [required_role, UserRole.ADMIN]:
            raise HTTPRolePermissionDeniedException

    return check_permission
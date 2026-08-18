from fastapi import Depends

from app.services.auth_service import AuthService, get_auth_service
from app.utils.security import get_token


def get_current_user_payload(
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.decode_access_token(token)

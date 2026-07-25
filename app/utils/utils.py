from fastapi import Depends

from app.services.auth_service import AuthService, get_auth_service
from app.utils.security import oauth_scheme


def get_current_user_payload(
    token: str = Depends(oauth_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.decode_access_token(token)

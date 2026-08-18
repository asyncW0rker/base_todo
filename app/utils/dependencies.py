from fastapi import Depends

from app.database.schemas import UserRole
from app.utils.rbac import role_permission_required, private_user_permission_required
from app.utils.security import get_token


auth_required = Depends(get_token)
admin_role_required = Depends(role_permission_required(UserRole.ADMIN))
manager_role_required = Depends(role_permission_required(UserRole.MANAGER))
user_ownership_required = Depends(private_user_permission_required)

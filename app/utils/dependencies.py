from fastapi import Depends

from app.database.schemas import UserRole
from app.utils.rbac import check_role_permission_dep, check_private_user_permission_dep
from app.utils.security import get_token


auth_required = Depends(get_token)
admin_role_required = Depends(check_role_permission_dep(UserRole.ADMIN))
manager_role_required = Depends(check_role_permission_dep(UserRole.MANAGER))
user_ownership_required = Depends(check_private_user_permission_dep)

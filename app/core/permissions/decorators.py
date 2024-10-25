
from functools import wraps
from typing import Optional
from fastapi import HTTPException, Request
from app.enums.users import Role, MenuPermissions
from sqlalchemy import select, and_

from app.models.users.users_model import Users, user_menus, user_parts

ROLE_LEVELS = {
    Role.MSO: 0,
    Role.SUPER_ADMIN: 1,
    Role.INTEGRATED_ADMIN: 10,
    Role.ADMIN: 20,
    Role.EMPLOYEE: 30,
    Role.ON_LEAVE: 40,
    Role.RESIGNED: 50,
}

def available_higher_than(minimum_role: Role):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                request = next((v for v in kwargs.values() if isinstance(v, Request)), None)
            
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")

            user = request.state.user

            if not user.role:
                raise HTTPException(status_code=401, detail="권한 정보가 없습니다.")

            print(f"Checking roles: user role={user.role}, minimum_role={minimum_role}")  # 역할 확인
            if ROLE_LEVELS[user.role] <= ROLE_LEVELS[minimum_role]: 
                print("Permission granted")  # 권한 승인
                return await func(*args, **kwargs)
            
            print("Permission denied")  # 권한 거부
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        return wrapper
    return decorator


async def can_manage_user_permissions(current_user: Users, target_user: Users) -> bool:
    """사용자가 다른 사용자의 권한을 관리할 수 있는지 확인"""
    if not current_user.role or not target_user.role:
        return False

    current_level = ROLE_LEVELS[current_user.role]
    target_level = ROLE_LEVELS[target_user.role]
    
    # MSO(1명)는 모든 지점의 모든 사용자 관리 가능
    if current_user.role == Role.MSO:
        return True
        
    # 최고 관리자는 자기 지점의, MSO가 아닌 사용자 관리 가능
    if current_user.role == Role.SUPER_ADMIN:
        return (current_user.branch_id == target_user.branch_id and 
                target_user.role != Role.MSO)
                
    # 통합 관리자는 자기 지점의, 자신보다 낮은 레벨의 같은 지점 사용자 관리 가능
    if current_user.role == Role.INTEGRATED_ADMIN:
        return (current_user.branch_id == target_user.branch_id and 
                target_level > current_level)
                
    return False
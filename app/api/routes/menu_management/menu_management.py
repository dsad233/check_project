from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import and_, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions.auth_utils import (
    available_higher_than,
    can_manage_user_permissions,
)
from app.enums.users import MenuPermissions, Role
from app.middleware.tokenVerify import get_current_user, validate_token
from app.models.users.users_model import Users, user_menus, user_parts
from app.models.parts.parts_model import Parts
from sqlalchemy.dialects.mysql import insert as mysql_insert
from app.service.menu_management_service import MenuService
from app.schemas.menu_management_schemas import ManageablePartsResponse, UpdateMenuPermissionsRequest
router = APIRouter()


@router.get(
    "/manageable-parts",
    response_model=ManageablePartsResponse,
    summary="관리 가능한 파트 목록 조회 - 파트관리자만 필요"
)
async def get_manageable_parts(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    파트 관리자가 관리할 수 있는 파트 목록을 조회합니다.
    통합 관리자의 경우 이 API를 호출할 필요가 없습니다.
    """
    menu_service = MenuService(db)
    parts = await menu_service.get_manageable_parts(current_user)
    return ManageablePartsResponse(parts=parts)

@router.get(
    "/{user_id}",
    summary="특정 사용자의 메뉴 권한 정보 조회"
)
async def get_user_menu_permissions(
    user_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """특정 사용자의 메뉴 권한 정보를 조회합니다."""
    menu_service = MenuService(db)
    return await menu_service.get_user_menu_permissions(user_id, current_user)


def get_menu_enum(menu_value: str) -> MenuPermissions:
    """메뉴 value에 해당하는 Enum 객체 반환"""
    try:
        return next(
            menu for menu in MenuPermissions if menu.value == menu_value
        )
    except StopIteration:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid menu name: {menu_value}. Available menus: {[e.value for e in MenuPermissions]}"
        )
@router.post("/update",
             summary="사용자 권한 관리",
             description="""
    사용자의 역할 변경 및 메뉴 권한을 설정합니다.
    
    [역할별 권한 관리 범위]
     1. MSO
       ✓ 역할 변경: 모든 사용자 가능
       ✓ 메뉴 세부 권한: 모든 권한 자동 부여 (permissions 불필요)
       
    2. 최고관리자 (자기 지점만)
       ✓ 역할 변경: 사원 ↔ 통합관리자/파트관리자
       ✓ 메뉴 세부 권한: 모든 권한 자동 부여 (permissions 불필요)
       
    3. 통합관리자 (자기 지점만)
       ✗ 역할 변경: 불가능
       ✓ 메뉴 세부 권한: 파트관리자만 수정 가능 (permissions 필수)
       
    4. 파트관리자
       ✗ 역할 변경: 불가능
       ✗ 메뉴 세부 권한: 불가능
    
    [요청 예시]
    1. MSO/최고관리자 승격 시:
    {
        "user_id": 123,
        "new_role": "MSO 최고권한"  // permissions 없어도 됨.
    }
    
    2. 통합/파트관리자 권한 설정/수정 시:
    {
        "user_id": 123,
        "new_role": "관리자",
        "permissions": [  // 필수 
            {
                "part_id": 1,
                "menu_name": "P.T관리",
                "is_permitted": true
            }
        ]
    }
    """,
             )
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_menu_permissions(
    request: Request,
    body: UpdateMenuPermissionsRequest,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    menu_service = MenuService(db)
    return await menu_service.update_menu_permissions(
        body.user_id,
        body.new_role,
        body.permissions,
        current_user
    )
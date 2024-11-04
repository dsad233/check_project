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


router = APIRouter()

class PartResponse(BaseModel):
    id: int
    name: str

class ManageablePartsResponse(BaseModel):
    parts: List[PartResponse]

#######

class MenuPermissionInfo(BaseModel):
    menu_name: str
    is_permitted: bool

class PartMenuPermissions(BaseModel):
    part_id: int
    part_name: str
    menu_permissions: List[MenuPermissionInfo]

class AdminMenuPermissionsResponse(BaseModel):
    menu_permissions: List[MenuPermissionInfo]

class PartAdminMenuPermissionsResponse(BaseModel):
    permissions: List[PartMenuPermissions]


class AdminNoPermissionsNeededResponse(BaseModel):
    message: str

#######


class MenuPermissionUpdate(BaseModel):
    part_id: int
    menu_name: str
    is_permitted: bool

class UpdateMenuPermissionsRequest(BaseModel):
    user_id: int
    new_role: Role #필수 필드로 변경
    permissions: Optional[List[MenuPermissionUpdate]] = None  # Optional로 변경
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
    try:
        if current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="파트 관리자만 접근 가능합니다."
            )

        # user_parts 테이블을 통해 파트 관리자의 파트들 조회
        query = select(Parts).join(
            user_parts,
            and_(
                user_parts.c.part_id == Parts.id,
                user_parts.c.user_id == current_user.id
            )
        ).where(
            and_(
                Parts.branch_id == current_user.branch_id,
                Parts.deleted_yn == "N"
            )
        )

        result = await db.execute(query)
        parts = result.scalars().all()

        if not parts:
            raise HTTPException(
                status_code=404,
                detail="관리 가능한 파트가 없습니다."
            )

        return ManageablePartsResponse(
            parts=[
                PartResponse(
                    id=part.id,
                    name=part.name
                ) for part in parts
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    try:
        target_user = await db.scalar(
            select(Users).where(Users.id == user_id)
        )

        if not target_user:
            raise HTTPException(
                status_code=404,
                detail="해당 사용자를 찾을 수 없습니다."
            )

        response = {
            "user_id": user_id,
            "user_role": target_user.role,
            "menu_permissions": []
        }

        # MSO/최고관리자
        if target_user.role in [Role.MSO, Role.SUPER_ADMIN]:
            response["menu_permissions"] = [
                {
                    "menu_name": menu.value,
                    "is_permitted": True
                } for menu in MenuPermissions
            ]
            return response

        # 통합관리자
        elif target_user.role == Role.INTEGRATED_ADMIN:
            menu_perms = await db.execute(
                select(user_menus)
                .join(Parts, user_menus.c.part_id == Parts.id)
                .where(
                    and_(
                        user_menus.c.user_id == user_id,
                        Parts.branch_id == target_user.branch_id  # 같은 지점의 파트만
                    )
                )
            )
            menu_perms = menu_perms.fetchall()

            response["menu_permissions"] = [
                {
                    "menu_name": menu.value,
                    "is_permitted": any(
                        p.is_permitted for p in menu_perms
                        if p.menu_name == menu
                    )
                } for menu in MenuPermissions
            ]
            return response

        # 파트관리자
        elif target_user.role == Role.ADMIN:
            manageable_parts = await db.scalars(
                select(Parts)
                .join(user_parts, user_parts.c.part_id == Parts.id)
                .where(
                    and_(
                        user_parts.c.user_id == user_id,
                        Parts.branch_id == target_user.branch_id,  # 같은 지점의 파트만
                        Parts.deleted_yn == "N"
                    )
                )
            )
            parts = manageable_parts.all()

            response["part_permissions"] = []
            for part in parts:
                menu_perms = await db.execute(
                    select(user_menus).where(
                        and_(
                            user_menus.c.user_id == user_id,
                            user_menus.c.part_id == part.id
                        )
                    )
                )
                menu_perms = menu_perms.fetchall()

                response["part_permissions"].append({
                    "part_id": part.id,
                    "part_name": part.name,
                    "menu_permissions": [
                        {
                            "menu_name": menu.value,
                            "is_permitted": next(
                                (p.is_permitted for p in menu_perms if p.menu_name == menu),
                                False
                            )
                        } for menu in MenuPermissions
                    ]
                })
            return response

        # 일반 사원 이하 등급 -> 일단 다 False로 리턴
        else:
            response["menu_permissions"] = [
                {
                    "menu_name": menu.value,
                    "is_permitted": False
                } for menu in MenuPermissions
            ]
            return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    # 함수를 라우터 밖으로 이동하고 들여쓰기 수정


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
        "new_role": "SUPER_ADMIN"  // permissions 없어도 됨.
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
    try:
        async def grant_full_permissions(user_id: int, part_id: int):
            """MSO/최고관리자 전체 권한 부여"""
            for menu in MenuPermissions:
                stmt = mysql_insert(user_menus).values(
                    user_id=user_id,
                    part_id=part_id,
                    menu_name=menu,
                    is_permitted=True
                )
                stmt = stmt.on_duplicate_key_update(
                    is_permitted=True
                )
                await db.execute(stmt)

        async def update_part_admin_permissions(user_id: int, permissions: List[MenuPermissionUpdate]):
            """파트 관리자 권한 설정"""
            for perm in permissions:
                # 파트가 해당 지점에 속하는지 확인
                part = await db.scalar(
                    select(Parts)
                    .where(
                        and_(
                            Parts.id == perm.part_id,
                            Parts.branch_id == target_user.branch_id,
                            Parts.deleted_yn == "N"
                        )
                    )
                )
                if not part:
                    raise HTTPException(
                        status_code=400,
                        detail=f"파트 ID {perm.part_id}는 해당 지점에 존재하지 않거나 삭제된 파트입니다."
                    )

                # user_parts 테이블 업데이트
                stmt = mysql_insert(user_parts).values(
                    user_id=user_id,
                    part_id=perm.part_id
                )
                stmt = stmt.prefix_with('IGNORE')
                await db.execute(stmt)

                # user_menus 테이블 업데이트
                menu_enum = get_menu_enum(perm.menu_name)
                stmt = mysql_insert(user_menus).values(
                    user_id=user_id,
                    part_id=perm.part_id,
                    menu_name=menu_enum,
                    is_permitted=perm.is_permitted
                )
                stmt = stmt.on_duplicate_key_update(
                    is_permitted=stmt.inserted.is_permitted
                )
                await db.execute(stmt)

        # 대상 사용자 조회
        target_user = await db.scalar(select(Users).where(Users.id == body.user_id))
        if not target_user:
            raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")

        # 권한 체크
        if body.permissions:
            for perm in body.permissions:
                if not await can_manage_user_permissions(
                        current_user, target_user, body.new_role, db, perm.part_id
                ):
                    raise HTTPException(status_code=401, detail="해당 사용자의 권한을 관리할 수 없습니다.")
        else:
            if not await can_manage_user_permissions(
                    current_user, target_user, body.new_role, db
            ):
                raise HTTPException(status_code=401, detail="해당 사용자의 권한을 관리할 수 없습니다.")

        # permissions 필수 체크 (통합관리자/파트관리자)
        if body.new_role in [Role.INTEGRATED_ADMIN, Role.ADMIN]:
            if not body.permissions:
                raise HTTPException(
                    status_code=400,
                    detail="통합관리자/파트관리자 설정 시 메뉴 권한(permissions) 설정이 필요합니다."
                )

        # 역할 변경
        if body.new_role != target_user.role:
            await db.execute(
                update(Users)
                .where(Users.id == target_user.id)
                .values(role=body.new_role)
            )

        # 권한 설정
        if body.new_role in [Role.MSO, Role.SUPER_ADMIN]:
            await grant_full_permissions(target_user.id, target_user.part_id)
        elif body.permissions:
            await update_part_admin_permissions(target_user.id, body.permissions)

        await db.commit()
        return {"message": "권한이 업데이트되었습니다"}

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException):
            raise e
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
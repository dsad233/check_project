from typing import List

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
    permissions: List[MenuPermissionUpdate]

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

@router.post("/update")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_menu_permissions(
    request: Request,
    body: UpdateMenuPermissionsRequest,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:

        def get_menu_enum(menu_value: str) -> MenuPermissions:
            """메뉴 value에 해당하는 Enum 객체 반환"""
            try:
                return next(
                    menu for menu in MenuPermissions if menu.value == menu_value
                )
            except StopIteration:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid menu name: {menu_value}. Available menus: {[e.value for e in MenuPermissions]}",
                )

        # 대상 사용자 조회
        target_user_query = await db.execute(
            select(Users).where(Users.id == body.user_id)
        )
        target_user = target_user_query.scalar_one_or_none()

        if not target_user:
            raise HTTPException(
                status_code=404, detail="해당 사용자를 찾을 수 없습니다."
            )

        # 권한 업데이트
        for perm in body.permissions:

            # target-user의 권한 관리 가능 여부 체크
            if not await can_manage_user_permissions(
                current_user, target_user, db, perm.part_id
            ):
                raise HTTPException(
                    status_code=403, detail="해당 사용자의 권한을 관리할 수 없습니다."
                )

            menu_enum = get_menu_enum(perm.menu_name)

            existing = await db.execute(
                select(user_menus).where(
                    and_(
                        user_menus.c.user_id == body.user_id,
                        user_menus.c.part_id == perm.part_id,
                        user_menus.c.menu_name == menu_enum,
                    )
                )
            )
            existing = existing.first()

            try:
                if existing:
                    await db.execute(
                        update(user_menus)
                        .where(
                            and_(
                                user_menus.c.user_id == target_user.id,
                                user_menus.c.part_id == perm.part_id,
                                user_menus.c.menu_name == menu_enum,
                            )
                        )
                        .values(is_permitted=perm.is_permitted)
                    )
                else:
                    await db.execute(
                        insert(user_menus).values(
                            user_id=target_user.id,
                            part_id=perm.part_id,
                            menu_name=menu_enum,
                            is_permitted=perm.is_permitted,
                        )
                    )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        await db.commit()
        return {"message": "메뉴 권한이 업데이트되었습니다"}

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

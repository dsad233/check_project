from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, insert
from typing import List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.permissions.auth_utils import available_higher_than, can_manage_user_permissions
from app.middleware.tokenVerify import get_current_user, validate_token
from app.models.users.users_model import Users, user_menus, user_parts
from app.enums.users import Role, MenuPermissions

router = APIRouter()

class MenuPermissionUpdate(BaseModel):
    part_id: int
    menu_name: str
    is_permitted: bool

class UpdateMenuPermissionsRequest(BaseModel):
    user_id: int
    permissions: List[MenuPermissionUpdate]

@router.post("/update") 
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_menu_permissions(
    request: Request,
    body: UpdateMenuPermissionsRequest, 
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        def get_menu_enum(menu_value: str) -> MenuPermissions:
            """메뉴 value에 해당하는 Enum 객체 반환"""
            try:
                return next(menu for menu in MenuPermissions if menu.value == menu_value)
            except StopIteration:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid menu name: {menu_value}. Available menus: {[e.value for e in MenuPermissions]}"
                )


        # 대상 사용자 조회
        target_user_query = await db.execute(
            select(Users).where(Users.id == body.user_id)
        )
        target_user = target_user_query.scalar_one_or_none()

        if not target_user:
            raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")


        # 권한 업데이트
        for perm in body.permissions:

            # target-user의 권한 관리 가능 여부 체크
            if not await can_manage_user_permissions(current_user, target_user,  db, perm.part_id):
                raise HTTPException(status_code=403, detail="해당 사용자의 권한을 관리할 수 없습니다.")


            menu_enum = get_menu_enum(perm.menu_name)

            existing = await db.execute(
                select(user_menus).where(
                    and_(
                        user_menus.c.user_id == body.user_id,
                        user_menus.c.part_id == perm.part_id,
                        user_menus.c.menu_name == menu_enum
                    )
                )
            )
            existing = existing.first()

            try:
                if existing:
                    await db.execute(
                        update(user_menus).where(
                            and_(
                                user_menus.c.user_id == target_user.id,
                                user_menus.c.part_id == perm.part_id,
                                user_menus.c.menu_name == menu_enum
                            )
                        ).values(is_permitted=perm.is_permitted)
                    )
                else:
                    await db.execute(
                        insert(user_menus).values(
                            user_id=target_user.id,
                            part_id=perm.part_id,
                            menu_name=menu_enum,
                            is_permitted=perm.is_permitted
                        )
                    )
            except Exception as e:
                print("Error details:", {
                    "error": str(e),
                    "menu_enum": menu_enum,
                    "menu_name": menu_enum.name,
                    "menu_value": menu_enum.value
                })
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
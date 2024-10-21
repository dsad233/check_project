from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update
from typing import List

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.api.routes.auth.auth import get_current_user
from app.models.users.users_model import Users, user_menus, user_parts
from app.models.menu_permission.menu_permission import UserMenuPermissionsUpdate, MenuPermissionUpdate
from app.middleware.permission import UserPermission
from app.models.parts.parts_model import Parts

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

@router.post("/update")
async def update_user_menu_permissions(
    update_data: UserMenuPermissionsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    사용자의 메뉴 권한을 업데이트합니다.
    이 API를 사용하려면 대상 사용자의 메뉴 권한을 변경할 수 있는 권한이 필요합니다.
    """
    user_permission = UserPermission(current_user['data'])

    async with db as session:
        try:
            target_user = await session.execute(select(Users).where(Users.id == update_data.user_id))
            target_user = target_user.scalar_one_or_none()

            if not target_user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            if not user_permission.can_edit_menu_permissions(target_user):
                raise HTTPException(status_code=403, detail="대상 사용자의 메뉴 권한을 변경할 권한이 없습니다.")

            # 사용자의 파트 확인
            user_parts_query = await session.execute(
                select(user_parts.c.part_id).where(user_parts.c.user_id == update_data.user_id)
            )
            user_part_ids = [row[0] for row in user_parts_query]

            for perm in update_data.permissions:
                if perm.part_id not in user_part_ids:
                    raise HTTPException(status_code=400, detail=f"사용자가 파트 ID {perm.part_id}에 속하지 않습니다.")

                # 기존 권한 확인 또는 새 권한 추가
                existing_perm = await session.execute(
                    select(user_menus).where(
                        (user_menus.c.user_id == update_data.user_id) &
                        (user_menus.c.part_id == perm.part_id) &
                        (user_menus.c.menu_name == perm.menu_name)
                    )
                )
                existing_perm = existing_perm.first()

                if existing_perm:
                    # 기존 권한 업데이트
                    await session.execute(
                        update(user_menus).where(
                            (user_menus.c.user_id == update_data.user_id) &
                            (user_menus.c.part_id == perm.part_id) &
                            (user_menus.c.menu_name == perm.menu_name)
                        ).values(is_permitted=perm.is_permitted)
                    )
                else:
                    # 새 권한 추가
                    await session.execute(
                        insert(user_menus).values(
                            user_id=update_data.user_id,
                            part_id=perm.part_id,
                            menu_name=perm.menu_name,
                            is_permitted=perm.is_permitted
                        )
                    )

            await session.commit()
            return {"message": "사용자의 메뉴 권한이 성공적으로 업데이트되었습니다."}

        except HTTPException as http_exc:
            await session.rollback()
            raise http_exc
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다: {str(e)}")
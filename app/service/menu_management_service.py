from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert as mysql_insert

from app.core.permissions.auth_utils import can_manage_user_permissions
from app.enums.users import MenuPermissions, Role
from app.models.users.users_model import Users, user_menus, user_parts
from app.models.parts.parts_model import Parts
from app.schemas.menu_management_schemas import MenuPermissionUpdate


class MenuService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_manageable_parts(self, current_user: Users):
        """파트 관리자가 관리할 수 있는 파트 목록을 조회"""
        if current_user.role != Role.ADMIN:
            raise HTTPException(status_code=403, detail="파트 관리자만 접근 가능합니다.")

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

        result = await self.db.execute(query)
        parts = result.scalars().all()

        if not parts:
            raise HTTPException(status_code=404, detail="관리 가능한 파트가 없습니다.")

        return [{"id": part.id, "name": part.name} for part in parts]

    async def get_user_menu_permissions(self, user_id: int, current_user: Users):
        """특정 사용자의 메뉴 권한 정보를 조회"""
        target_user = await self.db.scalar(select(Users).where(Users.id == user_id))
        if not target_user:
            raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")

        response = {
            "user_id": user_id,
            "user_role": target_user.role,
            "menu_permissions": []
        }

        # MSO/최고관리자
        if target_user.role in [Role.MSO, Role.SUPER_ADMIN]:
            response["menu_permissions"] = [
                {"menu_name": menu.value, "is_permitted": True}
                for menu in MenuPermissions
            ]
            return response

        # 통합관리자
        elif target_user.role == Role.INTEGRATED_ADMIN:
            menu_perms = await self.db.execute(
                select(user_menus)
                .join(Parts, user_menus.c.part_id == Parts.id)
                .where(
                    and_(
                        user_menus.c.user_id == user_id,
                        Parts.branch_id == target_user.branch_id
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
            manageable_parts = await self.db.scalars(
                select(Parts)
                .join(user_parts, user_parts.c.part_id == Parts.id)
                .where(
                    and_(
                        user_parts.c.user_id == user_id,
                        Parts.branch_id == target_user.branch_id,
                        Parts.deleted_yn == "N"
                    )
                )
            )
            parts = manageable_parts.all()

            response["part_permissions"] = []
            for part in parts:
                menu_perms = await self.db.execute(
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

        # 일반 사원 이하 등급
        else:
            response["menu_permissions"] = [
                {"menu_name": menu.value, "is_permitted": False}
                for menu in MenuPermissions
            ]
            return response

    def get_menu_enum(self, menu_value: str) -> MenuPermissions:
        """메뉴 value에 해당하는 Enum 객체 반환"""
        try:
            return next(menu for menu in MenuPermissions if menu.value == menu_value)
        except StopIteration:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid menu name: {menu_value}. Available menus: {[e.value for e in MenuPermissions]}"
            )

    async def update_menu_permissions(self, user_id: int, new_role: Role,
                                    permissions: Optional[List[MenuPermissionUpdate]], current_user: Users):
        """사용자 권한 관리"""
        try:
            target_user = await self.db.scalar(select(Users).where(Users.id == user_id))
            if not target_user:
                raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")

            # 권한 체크
            if permissions:
                for perm in permissions:
                    if not await can_manage_user_permissions(
                            current_user, target_user, new_role, self.db, perm.part_id
                    ):
                        raise HTTPException(status_code=401, detail="해당 사용자의 권한을 관리할 수 없습니다.")
            else:
                if not await can_manage_user_permissions(
                        current_user, target_user, new_role, self.db
                ):
                    raise HTTPException(status_code=401, detail="해당 사용자의 권한을 관리할 수 없습니다.")

            # permissions 필수 체크
            if new_role in [Role.INTEGRATED_ADMIN, Role.ADMIN] and not permissions:
                raise HTTPException(
                    status_code=400,
                    detail="통합관리자/파트관리자 설정 시 메뉴 권한(permissions) 설정이 필요합니다."
                )

            # 역할 변경
            if new_role != target_user.role:
                await self.db.execute(
                    update(Users)
                    .where(Users.id == target_user.id)
                    .values(role=new_role)
                )

            # 권한 설정
            if new_role in [Role.MSO, Role.SUPER_ADMIN]:
                await self._grant_full_permissions(target_user.id, target_user.part_id)
            elif permissions:
                await self.update_part_admin_permissions(target_user, permissions)

            await self.db.commit()
            return {"message": "권한이 업데이트되었습니다"}

        except Exception as e:
            await self.db.rollback()
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=str(e))

    async def _grant_full_permissions(self, user_id: int, part_id: int):
        """MSO/최고관리자 전체 권한 부여"""
        for menu in MenuPermissions:
            stmt = mysql_insert(user_menus).values(
                user_id=user_id,
                part_id=part_id,
                menu_name=menu,
                is_permitted=True
            )
            stmt = stmt.on_duplicate_key_update(is_permitted=True)
            await self.db.execute(stmt)

    async def update_part_admin_permissions(self, target_user: Users, permissions: List[MenuPermissionUpdate]):
        """파트 관리자 권한 설정"""
        for perm in permissions:
            part = await self.db.scalar(
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
                user_id=target_user.id,
                part_id=perm.part_id
            )
            stmt = stmt.prefix_with('IGNORE')
            await self.db.execute(stmt)

            # user_menus 테이블 업데이트
            menu_enum = self.get_menu_enum(perm.menu_name)
            stmt = mysql_insert(user_menus).values(
                user_id=target_user.id,
                part_id=perm.part_id,
                menu_name=menu_enum,
                is_permitted=perm.is_permitted
            )
            stmt = stmt.on_duplicate_key_update(
                is_permitted=stmt.inserted.is_permitted
            )
            await self.db.execute(stmt)
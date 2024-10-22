from typing import List
from app.models.parts.parts_model import Parts
from app.models.users.users_model import Users
from fastapi import HTTPException
from sqlalchemy import select

class UserPermission:
    def __init__(self, user):
        if isinstance(user, dict):
            user = Users(**user)
        self._user = user
        self.role = user.role
        self.part_id = user.part_id
        self.part_ids = [user.part_id] if user.part_id else []
        if self.role == "관리자":
            self.part_ids.extend([part.id for part in user.parts if part.id not in self.part_ids])
        self.branch_id = user.branch_id
        self.menu_permissions = {}
        self.part_menu_permissions = {}
        self.load_menu_permissions()

    def get_accessible_users_query(self, base_query, UserAlias):
        if self.role == "MSO 최고권한":
            return base_query
        elif self.role in ["최고관리자", "통합관리자"]:
            return base_query.filter(UserAlias.branch_id == self.branch_id)
        elif self.role == "관리자":
            return base_query.filter((UserAlias.part_id.in_(self.part_ids)) | 
                                     (UserAlias.parts.any(Parts.id.in_(self.part_ids))))
        elif self.role == "사원":
            return base_query.filter(UserAlias.part_id == self.part_id)
        else:  # 퇴사자, 휴직자
            return base_query.filter(UserAlias.id == self._user.id)

    def can_access_full_user_info(self, user):
        if self.role in ["MSO 최고권한", "최고관리자", "통합관리자"]:
            return True
        elif self.role == "관리자":
            return user.part_id in self.part_ids or any(part.id in self.part_ids for part in user.parts)
        else:
            return self._user.id == user.id

    def can_edit_user(self, target_user):
        if self._user.id == target_user.id:
            return True
        
        if self.role == "MSO 최고권한":
            return True
        elif self.role == "최고관리자":
            return target_user.role not in ["MSO 최고권한", "최고관리자"]
        elif self.role == "통합관리자":
            return target_user.role not in ["MSO 최고권한", "최고관리자", "통합관리자"]
        elif self.role == "관리자":
            if target_user.role in ["MSO 최고권한", "최고관리자", "통합관리자", "관리자"]:
                return False
            return target_user.part_id in self.part_ids or any(part.id in self.part_ids for part in target_user.parts)
        else:  # 사원, 퇴사자, 휴직자 등
            return self._user.id == target_user.id

    def can_delete_user(self, target_user):
        if self.role == "MSO 최고권한":
            return True
        elif self.role in ["최고관리자", "통합관리자"]:
            return target_user.branch_id == self.branch_id and target_user.role != "MSO 최고권한"
        elif self.role == "관리자":
            return (target_user.role not in ["MSO 최고권한", "최고관리자", "통합관리자"] and
                    (target_user.part_id in self.part_ids or any(part.id in self.part_ids for part in target_user.parts)))
        else:
            return False

    def can_edit_menu_permissions(self, target_user):
        if self.role == "MSO 최고권한":
            return True
        elif self.role == "최고관리자":
            return target_user.role != "MSO 최고권한" and self._user.branch_id == target_user.branch_id
        elif self.role == "통합관리자":
            return target_user.role not in ["MSO 최고권한", "최고관리자"] and self._user.branch_id == target_user.branch_id
        else:  # 관리자, 사원, 퇴사자, 휴직자 등
            return False

    def load_menu_permissions(self):
        for perm in self._user.part_menu_permissions:
            if perm.part_id not in self.part_menu_permissions:
                self.part_menu_permissions[perm.part_id] = {}
            self.part_menu_permissions[perm.part_id][perm.menu_permission_id] = perm.is_permitted

    def has_menu_permission(self, menu_name):
        if self.role == "MSO 최고권한":
            return True
        menu_permission = next((perm for perm in self._user.part_menu_permissions if perm.menu_permission.name == menu_name), None)
        if not menu_permission:
            return False
        for part_id in self.part_ids:
            if part_id in self.part_menu_permissions and menu_permission.menu_permission_id in self.part_menu_permissions[part_id]:
                return self.part_menu_permissions[part_id][menu_permission.menu_permission_id]
        return False

    def check_menu_permission(self, menu_name):
        if not self.has_menu_permission(menu_name):
            raise HTTPException(status_code=403, detail=f"{menu_name} 메뉴에 접근할 권한이 없습니다.")

    def __getattr__(self, name):
        return getattr(self._user, name)

    def dict(self):
        return {
            "role": self.role,
            "part_ids": self.part_ids,
            "branch_id": self.branch_id,
            "id": self._user.id,
        }
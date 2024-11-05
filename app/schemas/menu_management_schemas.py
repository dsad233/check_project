from typing import List, Optional
from pydantic import BaseModel
from app.enums.users import Role

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
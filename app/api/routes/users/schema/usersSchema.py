from pydantic import BaseModel
from typing import Optional

# 유저 수정 스키마
class UsersEdit(BaseModel):
    password : str
    nickname : str
    isOpen : Optional[bool] = None
    image : Optional[str] = None
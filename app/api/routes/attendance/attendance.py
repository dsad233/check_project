from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from app.core.database import async_session
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.users_model import Users
from app.middleware.tokenVerify import validate_token, get_current_user


router = APIRouter(dependencies=[Depends(validate_token)])
attendance = async_session()

# 근로 관리 전체 조회
@router.get('/{branch_id}/parts/{part_id}/attendance')
async def find_attendance(branch_id : int, part_id : int, token=Annotated[Users, Depends(get_current_user)]):
    try:
        find_attendance = await attendance.execute(select(Users))
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail= "근태 관리 전체 조회에 실패하였습니다.")
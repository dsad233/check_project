from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from app.core.database import async_session
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.users_model import Users
from app.models.branches.work_policies_model import WorkPolicies
from app.middleware.tokenVerify import validate_token, get_current_user


router = APIRouter(dependencies=[Depends(validate_token)])
attendance = async_session()

# 근로 관리 전체 조회
@router.get('/{branch_id}/parts/{part_id}/attendance')
async def find_attendance(branch_id : int, part_id : int, token:Annotated[Users, Depends(get_current_user)]):
    try:
        find_part = await attendance.execute(select(Parts).where(Parts.id == part_id))
        
        result_part = find_part.scalar_one_or_none()
        

        
        find_attendance = await attendance.execute(select(Users).where(Branches.id == branch_id, Branches.name))

        # find_working = await attendance.execute(select(WorkPolicies).where(WorkPolicies.))
    except Exception as err:

        raise HTTPException(status_code=500, detail= "근태 관리 전체 조회에 실패하였습니다.")
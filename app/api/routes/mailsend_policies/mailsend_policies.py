from fastapi import APIRouter, HTTPException, Depends
from app.models.users.users_model import Users
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.middleware.tokenVerify import validate_token, get_current_user
from app.core.database import async_session
from typing import Annotated
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, load_only


router = APIRouter(dependencies=[Depends(validate_token)])
mailsend = async_session()

# 메일 발송 기록 전체 조회
@router.get("/{branch_id}/mailsend")
async def get_send_all_user(token:Annotated[Users, Depends(get_current_user)]):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email)))
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송된 인원 전체 조회에 실패하였습니다.")
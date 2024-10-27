from fastapi import APIRouter, HTTPException, Depends
from app.middleware.tokenVerify import validate_token, get_current_user
from app.core.database import async_session
from app.models.users.users_model import Users
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.overtimes_model import Overtimes
from app.models.branches.overtime_policies_model import OverTimePolicies
from sqlalchemy import select
from sqlalchemy.orm import load_only



router = APIRouter(dependencies=[Depends(validate_token)])
overtime_history = async_session()


# O.T 승인 내역 전체 조회
@router.get("/overtime-history")
async def get_all_overtime_history(skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_application = await overtime_history.scalars(select(Overtimes).join(Users, Users.id == Overtimes.applicant_id, Overtimes.overtime_hours == "30").options(load_only(Overtimes.applicant_id, Overtimes.overtime_hours)))
        result = find_overtime_application.all()

        find_overtime_history = await overtime_history.execute(select(Users, Branches, Parts, Overtimes, OverTimePolicies).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(OverTimePolicies.branch_id == Branches.id).options(load_only(Users.name, Users.gender, Users.resignation_date), load_only(Branches.name), load_only(Parts.name), load_only(OverTimePolicies.common_ot_30, OverTimePolicies.common_ot_60, OverTimePolicies.common_ot_90, OverTimePolicies.common_ot_120, OverTimePolicies.doctor_ot_30, OverTimePolicies.doctor_ot_60, OverTimePolicies.doctor_ot_90, OverTimePolicies.doctor_ot_120)))
        result = find_overtime_history

        return { "message" : "성공적으로 O.T 승인 내역 전체 조회를 완료하였습니다.", "data" : result }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"O.T 승인 내역 전체 조회에 실패하였습니다. Error : {err}")
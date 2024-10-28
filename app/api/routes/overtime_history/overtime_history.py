from fastapi import APIRouter, HTTPException, Depends
from app.middleware.tokenVerify import validate_token, get_current_user
from app.core.database import async_session
from app.models.users.users_model import Users
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.overtimes_model import Overtimes, OverTime_History
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

        # find_overtime_application = await overtime_history.scalars(select(Overtimes).join(Users, Users.id == Overtimes.applicant_id, Overtimes.overtime_hours == "30").options(load_only(Overtimes.applicant_id, Overtimes.overtime_hours)))
        # result = find_overtime_application.all()
        
        # find_overtime_application = await overtime_history.scalars(select(OverTime_History).where(OverTime_History.user_id == Users.id, OverTime_History.deleted_at == "N"))

        find_overtime_history = await overtime_history.execute(select(Users, Branches, Parts, Overtimes, OverTimePolicies).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(OverTimePolicies.branch_id == Branches.id).options(load_only(Users.name, Users.gender, Users.resignation_date), load_only(Branches.name), load_only(Parts.name), load_only(OverTimePolicies.common_ot_30, OverTimePolicies.common_ot_60, OverTimePolicies.common_ot_90, OverTimePolicies.doctor_ot_30, OverTimePolicies.doctor_ot_60, OverTimePolicies.doctor_ot_90)).where(Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N", OverTimePolicies.deleted_yn == "N"))
        result = find_overtime_history.all()

        fetch_data = [
            {
                "users" : { "user_id" : data.Users.id, "user_name" : data.Users.name, "user_gender" : data.Users.gender, "user_resignation_date" : data.Users.resignation_date },
                "branches" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "parts" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "overtime_history" : { "overtime_histroy_id" : data.OverTime_History.id, "overtime_histroy_common_ot_30" : data.OverTimePolicies.common_ot_30, "overtime_histroy_common_ot_60" : data.OverTimePolicies.common_ot_60, "overtime_histroy_common_ot_90" : data.OverTimePolicies.common_ot_90 },
                "overtime_history_is_doctor" : { "overtime_histroy_doctor_ot_30" : data.OverTimePolicies.doctor_ot_30, "overtime_histroy_doctor_ot_60" : data.OverTimePolicies.doctor_ot_60, "overtime_histroy_doctor_ot_90" : data.OverTimePolicies.doctor_ot_90 }
            }
            for data in result
        ]

        return { "message" : "성공적으로 O.T 승인 내역 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"O.T 승인 내역 전체 조회에 실패하였습니다. Error : {err}")
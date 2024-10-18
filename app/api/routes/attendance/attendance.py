from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from app.core.database import async_session
from app.models.branches.allowance_policies_model import AllowancePolicies
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.users_model import Users
from app.models.branches.work_policies_model import WorkPolicies
from app.models.users.overtimes_model import Overtimes
from app.models.attendance.attendance_model import AttendanceCreate, Attendance
from app.models.commutes.commutes_model import Commutes
from app.models.users.leave_histories_model import LeaveHistories
from app.models.branches.overtime_policies_model import OverTimePolicies
from app.middleware.tokenVerify import validate_token, get_current_user
from sqlalchemy.orm import joinedload


router = APIRouter(dependencies=[Depends(validate_token)])
attendance = async_session()

# 근로 관리 생성
@router.get('/{branch_id}/parts/{part_id}/attendance/users/{user_id}')
async def find_attendance(branch_id : int, part_id : int, user_id : int, token:Annotated[Users, Depends(get_current_user)], attendanceCreate : AttendanceCreate):
    try:

        find_data = await attendance.execute(select(Parts).join(Branches, Parts, Overtimes, WorkPolicies))


        find_branch = await attendance.execute(select(Branches).where(Branches.id == branch_id, Branches.deleted_yn == "N"))
        result_branch = find_branch.scalar_one_or_none()

        if(result_branch == None):
            raise HTTPException(status_code=404, detail="지점 데이터가 존재하지 않습니다.")

        find_part = await attendance.execute(select(Parts).where(Parts.id == part_id, Parts.deleted_yn == "N"))
        result_part = find_part.scalar_one_or_none()

        if(result_part == None):
            raise HTTPException(status_code=404, detail="파트 데이터가 존재하지 않습니다.")
        
        find_overtimes = await attendance.execute(select(Overtimes).where(Overtimes.applicant_id == user_id))
        
        result_overtime = find_overtimes.scalar_one_or_none()

        if(result_overtime == None):
            raise HTTPException(status_code=404, detail="오버타임 데이터가 존재하지 않습니다.")
        
        find_user  = await attendance.execute(select(Users).where(Users.id == user_id))
        resutl_user = find_user.scalar_one_or_none()

        if(resutl_user == None):
            raise HTTPException(status_code=404, detail="유저 데이터가 존재하지 않습니다.")
        

        
        find_attendance = await attendance.execute(select(Users).where(Branches.id == branch_id, Branches.name))

        # new_attendance = Attendance(
        #     branch_id = result_branch.id,
        #     part_id = result_part.id,
        #     branch_name = result_branch.name,
        #     name = resutl_user.name,
        #     gender = resutl_user.gender,
        #     part_name = result_part.name,
        #     workdays = 
        # )

        # find_working = await attendance.execute(select(WorkPolicies).where(WorkPolicies.))
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail= "근태 관리 생성에 실패하였습니다.")
    


    

@router.get('/attendance')
async def find_attendance(token: Annotated[Users, Depends(get_current_user)]):
    try:
        find_attendance = await attendance.execute(
            select(Users, Branches, Parts, Commutes, LeaveHistories, Overtimes)
            .join(Branches, Users.branch_id == Branches.id)
            .join(Parts, Users.part_id == Parts.id)
            .outerjoin(Commutes, Users.id == Commutes.user_id)
            .outerjoin(LeaveHistories, Users.id == LeaveHistories.user_id)
            .outerjoin(Overtimes, Users.id == Overtimes.applicant_id)
        )
        result = find_attendance.fetchall()
        
        attendance_data = []
        for user, branch, part, commute, leave, overtime in result:
            attendance_info = {
                "번호": user.id,
                "지점": branch.name,
                "이름": user.name,
                "근무파트": part.name,
                "근무일수": commute.work_days if commute else 0,
                "휴일근무": commute.holiday_work_days if commute else 0,
                "정규 휴무": leave.regular_leave_days if leave else 0,
                "연차 사용": leave.annual_leave_days if leave else 0,
                "무급 사용": leave.unpaid_leave_days if leave else 0,
                "계획 근무": "0일",  # 데이터 없음, 필요시 추가
                "휴일 근무": "0일",  # 데이터 없음, 필요시 추가
                "추가 근무 시간": "0시간",  # 데이터 없음, 필요시 추가
                "추가 근무 수당": 0,
                "O.T 30분 할증": overtime.ot_30min if overtime else 0,
                "O.T 60분 할증": overtime.ot_60min if overtime else 0,
                "O.T 90분 할증": overtime.ot_90min if overtime else 0,
                "O.T 총 금액": overtime.total_amount if overtime else 0
            }
            attendance_data.append(attendance_info)
        
        return {"message": "성공적으로 근로 관리 전체 조회를 완료하였습니다.", "data": attendance_data}
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="근태 관리 전체 조회에 실패하였습니다.")

@router.post('/attendance')
async def create_attendance(token: Annotated[Users, Depends(get_current_user)], attendance_data: AttendanceCreate):
    try:
        new_attendance = Attendance(
            user_id=attendance_data.user_id,
            branch_id=attendance_data.branch_id,
            part_id=attendance_data.part_id,
            work_days=attendance_data.work_days,
            holiday_work_days=attendance_data.holiday_work_days,
            regular_leave_days=attendance_data.regular_leave_days,
            annual_leave_days=attendance_data.annual_leave_days,
            unpaid_leave_days=attendance_data.unpaid_leave_days,
            planned_work_days=attendance_data.planned_work_days,
            additional_work_hours=attendance_data.additional_work_hours,
            additional_work_pay=attendance_data.additional_work_pay,
            ot_30min=attendance_data.ot_30min,
            ot_60min=attendance_data.ot_60min,
            ot_90min=attendance_data.ot_90min,
            ot_total_amount=attendance_data.ot_total_amount
        )

        attendance.add(new_attendance)
        await attendance.commit()
        await attendance.refresh(new_attendance)

        return {"message": "근태 정보가 성공적으로 생성되었습니다.", "data": new_attendance}
    except Exception as err:
        await attendance.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="근태 정보 생성에 실패하였습니다.")

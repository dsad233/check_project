from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from app.core.database import async_session
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.users_model import Users
from app.models.branches.work_policies_model import WorkPolicies
from app.models.users.overtimes_model import Overtimes
from app.models.attendance.attendance_model import AttendanceCreate, Attendance
from app.middleware.tokenVerify import validate_token, get_current_user


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

        raise HTTPException(status_code=500, detail= "근태 관리 생성에 실패하였습니다.")
    


    
    
# 근로 관리 전체 조회
@router.get('/attendance')
async def find_attendance(token:Annotated[Users, Depends(get_current_user)]):
    try:
        find_attendance = await attendance.execute(select(Attendance).offset(0).limit(100))
        result_find = find_attendance.scalars().all()

        if(len(result_find) == 0):
            raise HTTPException("근태 관리 정보들이 존재하지 않습니다.")
        
        return { "message" : "성공적으로 근로 관리 전체 조회를 완료 하였습니다.", "data" : result_find }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="근태 관리 전체 조회에 실패하였습니다.")
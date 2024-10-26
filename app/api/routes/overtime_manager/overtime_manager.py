from calendar import monthrange
from datetime import datetime, date, timedelta
from fastapi import APIRouter, HTTPException, Depends
from app.core.database import async_session
from app.models.users.overtimes_model import Overtimes
from app.models.users.users_model import Users
from app.models.parts.parts_model import Parts
from app.models.branches.branches_model import Branches
from app.middleware.tokenVerify import validate_token, get_current_user
from sqlalchemy.future import select
from sqlalchemy.orm import load_only


router = APIRouter(dependencies=[Depends(validate_token)])
overtime_manager = async_session()


# 오버타임 관리 전체 조회 [최고 관리자]
@router.get("/overtime-manager", summary= "오버타임 관리 전체 조회")
async def get_all_overtime_manager(skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 전체 조회에 오류가 발생하였습니다. Error : {err}")
    
# 오버타임 관리 승인완료 전체 조회 [최고 관리자]
@router.get("/overtime-manager/approved", summary= "오버타임 관리 승인완료 전체 조회")
async def get_approved_all_overtime_manager(skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "approved", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 승인완료 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 승인완료 전체 조회에 오류가 발생하였습니다. Error : {err}")
    
    
# 오버타임 관리 반려중 전체 조회 [최고 관리자]
@router.get("/overtime-manager/rejected", summary= "오버타임 관리 반려중 전체 조회")
async def get_rejected_all_overtime_manager(skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "rejected", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 반려중 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 반려중 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 오버타임 관리 월간 전체 조회 [최고 관리자]
@router.get("/overtime-manager/month", summary= "오버타임 관리 월간별 전체 조회")
async def get_month_all_overtime_manager(date : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)


        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= date_start_day, Overtimes.application_date <= date_end_day, Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 월간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 월간별 전체 조회에 오류가 발생하였습니다. Error : {err}")
    
    
# 오버타임 관리 주간 전체 조회 [최고 관리자]
@router.get("/overtime-manager/week", summary= "오버타임 관리 주간별 전체 조회")
async def get_week_all_overtime_manager(date : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        
        # 해당 주의 일요일 찾기 (주의 시작일)
        start_of_week = date_obj - timedelta(days=date_obj.weekday() + 1)
        if start_of_week.month != date_obj.month:
            start_of_week = date_obj.replace(day=1)
        
        # 해당 주의 토요일 찾기 (주의 마지막 날)
        end_of_week = start_of_week + timedelta(days=6)
        _, last_day = monthrange(date_obj.year, date_obj.month)
        if end_of_week.day > last_day:
            end_of_week = date_obj.replace(day=last_day)

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= start_of_week, Overtimes.application_date <= end_of_week, Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 주간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 주간별 전체 조회에 오류가 발생하였습니다. Error : {err}")
    
    
# 오버타임 관리 이름별 전체 조회 [최고 관리자]
@router.get("/overtime-manager/search/name", summary= "오버타임 관리 이름별 전체 조회")
async def get_name_all_overtime_manager(name : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Users.name.like(f'%{name}%'), Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 이름별 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 이름별 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 오버타임 관리 전화번호별 전체 조회 [최고 관리자]
@router.get("/overtime-manager/search/phonenumber", summary= "오버타임 관리 전화번호별 전체 조회")
async def get_phone_number_all_overtime_manager(phone_number : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Users.phone_number.like(f'%{phone_number}%'), Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N", Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 전화번호별 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 전화번호별 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 오버타임 관리 상태별 전체 조회[최고 관리자]
@router.get("/overtime-manager/filter/status", summary= "오버타임 관리 상태별 전체 조회")
async def get_status_all_overtime_manager(status : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == status, Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 상태별 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 상태별 전체 조회에 오류가 발생하였습니다. Error : {err}")


""" 지점별 """

# 지점별 오버타임 관리 전체 조회 [관리자]
router.get('/{branch_id}/overtime-manager', summary="오버타임 관리 지점별 전체 조회")
async def get_branch_all_overtime_manager(branch_id : int, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 지점별 오버타임 승인완료 관리 전체 조회 [관리자]
router.get('/{branch_id}/overtime-manager/approved', summary="오버타임 관리 지점별 승인완료 전체 조회")
async def get_branch_approved_all_overtime_manager(branch_id : int, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "approved", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 승인완료 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 승인완료 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 지점별 오버타임 반려중 관리 전체 조회 [관리자]
router.get('/{branch_id}/overtime-manager/rejected', summary="오버타임 관리 지점별 반려중 전체 조회")
async def get_branch_rejected_all_overtime_manager(branch_id : int, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "rejected", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 반려중 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 반려중 전체 조회에 오류가 발생하였습니다. Error : {err}")


# 지점별 오버타임 월간 전체 조회 [관리자]
router.get('/{branch_id}/overtime-manager/month', summary="오버타임 관리 지점별 월간 전체 조회")
async def get_branch_month_all_overtime_manager(branch_id : int, date : date, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)
        
        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= date_start_day, Overtimes.application_date <= date_end_day, Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 월간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 월간 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 지점별 오버타임 주간 전체 조회 [관리자]
router.get('/{branch_id}/overtime-manager/week', summary="오버타임 관리 지점별 주간 전체 조회")
async def get_branch_week_all_overtime_manager(branch_id : int, date : date, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        
        # 해당 주의 일요일 찾기 (주의 시작일)
        start_of_week = date_obj - timedelta(days=date_obj.weekday() + 1)
        if start_of_week.month != date_obj.month:
            start_of_week = date_obj.replace(day=1)
        
        # 해당 주의 토요일 찾기 (주의 마지막 날)
        end_of_week = start_of_week + timedelta(days=6)
        _, last_day = monthrange(date_obj.year, date_obj.month)
        if end_of_week.day > last_day:
            end_of_week = date_obj.replace(day=last_day)
        
        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches.id == Users.branch_id).join(Parts.id == Users.part_id).join(Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Overtimes.application_date >= start_of_week, Overtimes.application_date <= end_of_week, Overtimes.status == "pending",Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 주간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 주간 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 지점별 오버타임 관리 이름별 전체 조회 [관리자]
@router.get("/{branch_id}/overtime-manager/search/name", summary= "오버타임 관리 지점별 이름 전체 조회")
async def get_branch_name_all_overtime_manager(branch_id : int, name : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Users.name.like(f'%{name}%'), Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 이름별 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 이름별 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 지점별 오버타임 관리 전화번호별 전체 조회 [관리자]
@router.get("/{branch_id}/overtime-manager/search/phonenumber", summary= "오버타임 관리 지점별 전화번호 전체 조회")
async def get_branch_phone_number_all_overtime_manager(branch_id : int, phone_number : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Users.phone_number.like(f'%{phone_number}%'), Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N", Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 전화번호 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 전화번호 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 지점별 오버타임 관리 상태별 전체 조회[최고 관리자]
@router.get("/{branch_id}/overtime-manager/filter/status", summary= "오버타임 관리 지점별 상태 전체 조회")
async def get_branch_status_all_overtime_manager(branch_id : int, status : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == status, Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 상태 정보 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 상태 정보 전체 조회에 오류가 발생하였습니다. Error : {err}")
    


""" 파트별 """

# 파트별 오버타임 관리 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager", summary= "오버타임 관리 파트별 전체 조회")
async def get_part_all_overtime_manager(branch_id : int, part_id : int, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 파트별 오버타임 승인완료 관리 전체 조회 [관리자]
router.get('/{branch_id}/parts/{part_id}/overtime-manager/approved', summary="오버타임 관리 파트별 승인완료 전체 조회")
async def get_part_approved_all_overtime_manager(branch_id : int, part_id : int, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "approved", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 승인완료 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 승인완료 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 파트별 오버타임 반려중 관리 전체 조회 [관리자]
router.get('/{branch_id}/parts/{part_id}/overtime-manager/rejected', summary="오버타임 관리 파트별 반려중 전체 조회")
async def get_part_rejected_all_overtime_manager(branch_id : int, part_id : int, dskip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "rejected", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 반려중 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 반려중 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 파트별 오버타임 관리 월간 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager/month", summary= "오버타임 관리 파트별 월간 전체 조회")
async def get_part_month_all_overtime_manager(branch_id : int, part_id : int, date : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)


        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= date_start_day, Overtimes.application_date <= date_end_day, Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 월간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 월간 전체 조회에 오류가 발생하였습니다. Error : {err}")
    
    
# 파트별 오버타임 관리 주간 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager/week", summary= "오버타임 관리 파트별 주간 전체 조회")
async def get_part_week_all_overtime_manager(branch_id : int, part_id : int, date : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        
        # 해당 주의 일요일 찾기 (주의 시작일)
        start_of_week = date_obj - timedelta(days=date_obj.weekday() + 1)
        if start_of_week.month != date_obj.month:
            start_of_week = date_obj.replace(day=1)
        
        # 해당 주의 토요일 찾기 (주의 마지막 날)
        end_of_week = start_of_week + timedelta(days=6)
        _, last_day = monthrange(date_obj.year, date_obj.month)
        if end_of_week.day > last_day:
            end_of_week = date_obj.replace(day=last_day)

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= start_of_week, Overtimes.application_date <= end_of_week, Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 주간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 주간 전체 조회에 오류가 발생하였습니다. Error : {err}")
    
    
# 파트별 오버타임 관리 이름별 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager/search/name", summary= "오버타임 관리 이름별 전체 조회")
async def get_part_name_all_overtime_manager(branch_id : int, part_id : int, name : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Parts.id == part_id, Users.name.like(f'%{name}%'), Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 이름 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 이름 전체 조회에 오류가 발생하였습니다. Error : {err}")
    

# 파트별 오버타임 관리 전화번호별 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager/search/phonenumber", summary= "오버타임 관리 파트별 전화번호 전체 조회")
async def get_part_phone_number_all_overtime_manager(branch_id : int, part_id : int, phone_number : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Parts.id == part_id, Users.phone_number.like(f'%{phone_number}%'), Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N", Overtimes.status == "pending", Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 전화번호 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 전화번호 전체 조회에 오류가 발생하였습니다. Error : {err}")
    


# 지점별 오버타임 관리 상태별 전체 조회[최고 관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager/filter/status", summary= "오버타임 관리 지점별 상태 전체 조회")
async def get_part_status_all_overtime_manager(branch_id : int, part_id : int, status : str, skip: int = 0, limit: int = 10, page: int = 1):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status)).where(Branches.id == branch_id, Parts.id == part_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.status == status, Overtimes.deleted_yn == "N").offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id , "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_is_approved" : data.Overtimes.is_approved }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 상태 정보 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 상태 정보 전체 조회에 오류가 발생하였습니다. Error : {err}")




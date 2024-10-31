from calendar import monthrange
from datetime import datetime, date, timedelta
from fastapi import APIRouter, HTTPException, Depends
from app.core.database import async_session, get_db
from app.models.users.overtimes_model import Overtimes
from app.models.users.users_model import Users
from app.models.parts.parts_model import Parts
from app.models.branches.branches_model import Branches
from app.middleware.tokenVerify import validate_token, get_current_user
from sqlalchemy.future import select
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()
# overtime_manager = async_session()


# 오버타임 관리 전체 조회 [최고 관리자]
@router.get("/overtime-manager", summary= "오버타임 관리 전체 조회")
async def get_all_overtime_manager(
    skip: int = 0,
    limit: int = 10,
    page: int = 1,
    overtime_manager: AsyncSession = Depends(get_db)
    ):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.deleted_yn == "N").order_by(Overtimes.application_date.desc()).offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()
     

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    

# 오버타임 관리 필터 전체 조회 [최고 관리자]
@router.get("/overtime-manager/filter", summary= "오버타임 관리 필터 전체 조회")
async def get_filter_all_overtime_manager(
    skip: int = 0,
    limit: int = 10,
    page: int = 1,
    name: str = None,
    phone_number: str = None,
    branch_name: str = None,
    part_name: str = None,
    status: str = None,
    overtime_manager: AsyncSession = Depends(get_db)):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        base_query = (select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.deleted_yn == "N"))

        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        if phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        if branch_name:
            base_query = base_query.where(Branches.name.like(f"%{branch_name}%"))
        if part_name:
            base_query = base_query.where(Parts.name.like(f"%{part_name}%"))
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))


        base_query = base_query.order_by(Overtimes.application_date.desc()).offset(skip).limit(limit)

        find_overtime_list = await overtime_manager.execute(base_query)
        result_overtime = find_overtime_list.fetchall()
     

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 필터 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 필터 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    
# 오버타임 관리 월간 전체 조회 [최고 관리자]
@router.get("/overtime-manager/month", summary= "오버타임 관리 월간별 전체 조회")
async def get_month_all_overtime_manager(
    date : str,
    skip: int = 0,
    limit: int = 10,
    page: int = 1,
    name: str = None,
    phone_number: str = None,
    branch_name: str = None,
    part_name: str = None,
    status: str = None,
    overtime_manager: AsyncSession = Depends(get_db)
):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)


        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= date_start_day, Overtimes.application_date <= date_end_day, Overtimes.deleted_yn == "N").order_by(Overtimes.application_date.desc()).offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 월간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 월간별 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    
    
# 오버타임 관리 월간 필터 전체 조회 [최고 관리자]
@router.get("/overtime-manager/month/filter", summary= "오버타임 관리 월간별 필터 전체 조회")
async def get_month_filter_all_overtime_manager(
    date : str,
    skip: int = 0,
    limit: int = 10,
    page: int = 1,
    name: str = None,
    phone_number: str = None,
    branch_name: str = None,
    part_name: str = None,
    status: str = None,
    overtime_manager: AsyncSession = Depends(get_db)
    ):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        base_query = select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= date_start_day, Overtimes.application_date <= date_end_day, Overtimes.deleted_yn == "N")

        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        if phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        if branch_name:
            base_query = base_query.where(Branches.name.like(f"%{branch_name}%"))
        if part_name:
            base_query = base_query.where(Parts.name.like(f"%{part_name}%"))
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))


        base_query = base_query.order_by(Overtimes.application_date.desc()).offset(skip).limit(limit)

        find_overtime_list = await overtime_manager.execute(base_query)
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 월간별 필터 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 월간별 필터 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    
    
# 오버타임 관리 주간 전체 조회 [최고 관리자]
@router.get("/overtime-manager/week", summary= "오버타임 관리 주간별 전체 조회")
async def get_week_all_overtime_manager(
    date : str,
    skip: int = 0,
    limit: int = 10,
    page: int = 1,
    overtime_manager: AsyncSession = Depends(get_db)
):
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

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= start_of_week, Overtimes.application_date <= end_of_week, Overtimes.deleted_yn == "N").order_by(Overtimes.application_date.desc()).offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 주간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 주간별 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    


    # 오버타임 관리 주간 필터 전체 조회 [최고 관리자]
@router.get("/overtime-manager/week/filter", summary= "오버타임 관리 주간별 필터 전체 조회")
async def get_week_filter_all_overtime_manager(date : str, skip: int = 0, limit: int = 10, page: int = 1, name: str = None, phone_number: str = None, branch_name: str = None, part_name: str = None, status: str = None,overtime_manager: AsyncSession = Depends(get_db)):
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

        base_query = select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= start_of_week, Overtimes.application_date <= end_of_week, Overtimes.deleted_yn == "N")

        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        if phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        if branch_name:
            base_query = base_query.where(Branches.name.like(f"%{branch_name}%"))
        if part_name:
            base_query = base_query.where(Parts.name.like(f"%{part_name}%"))
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))


        base_query = base_query.order_by(Overtimes.application_date.desc()).offset(skip).limit(limit)

        find_overtime_list = await overtime_manager.execute(base_query)
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 주간별 필터 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 주간별 필터 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")


""" 지점별 """

# 지점별 오버타임 관리 전체 조회 [관리자]
@router.get('/{branch_id}/overtime-manager', summary="오버타임 관리 지점별 전체 조회")
async def get_branch_all_overtime_manager(branch_id : int, skip: int = 0, limit: int = 10, page: int = 1, overtime_manager: AsyncSession = Depends(get_db)):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.deleted_yn == "N").order_by(Overtimes.application_date.desc()).offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    

# 지점별 오버타임 관리 필터 전체 조회 [관리자]
@router.get('/{branch_id}/overtime-manager/filter', summary="오버타임 관리 지점별 필터 전체 조회")
async def get_branch_all_overtime_manager(branch_id : int, skip: int = 0, limit: int = 10, page: int = 1, name: str = None, phone_number: str = None, branch_name: str = None, part_name: str = None, status: str = None, overtime_manager: AsyncSession = Depends(get_db)):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        base_query = select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.deleted_yn == "N")

        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        if phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        if branch_name:
            base_query = base_query.where(Branches.name.like(f"%{branch_name}%"))
        if part_name:
            base_query = base_query.where(Parts.name.like(f"%{part_name}%"))
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))


        base_query = base_query.order_by(Overtimes.application_date.desc()).offset(skip).limit(limit)

        find_overtime_list = await overtime_manager.execute(base_query)
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 필터 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 필터 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")


# 지점별 오버타임 월간 전체 조회 [관리자]
@router.get('/{branch_id}/overtime-manager/month', summary="오버타임 관리 지점별 월간 전체 조회")
async def get_branch_month_all_overtime_manager(branch_id : int, date : str, skip: int = 0, limit: int = 10, page: int = 1, overtime_manager: AsyncSession = Depends(get_db)):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)
        
        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= date_start_day, Overtimes.application_date <= date_end_day, Overtimes.deleted_yn == "N").order_by(Overtimes.application_date.desc()).offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 월간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 월간 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    

# 지점별 오버타임 월간 필터 전체 조회 [관리자]
@router.get('/{branch_id}/overtime-manager/month/filter', summary="오버타임 관리 지점별 월간 필터 전체 조회")
async def get_branch_month_all_overtime_manager(branch_id : int, date : str, skip: int = 0, limit: int = 10, page: int = 1, name: str = None, phone_number: str = None, branch_name: str = None, part_name: str = None, status: str = None, overtime_manager: AsyncSession = Depends(get_db)):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        base_query = select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= date_start_day, Overtimes.application_date <= date_end_day, Overtimes.deleted_yn == "N")

        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        if phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        if branch_name:
            base_query = base_query.where(Branches.name.like(f"%{branch_name}%"))
        if part_name:
            base_query = base_query.where(Parts.name.like(f"%{part_name}%"))
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))


        base_query = base_query.order_by(Overtimes.application_date.desc()).offset(skip).limit(limit)
        
        find_overtime_list = await overtime_manager.execute(base_query)
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 월간 필터 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 월간 필터 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    

# 지점별 오버타임 주간 전체 조회 [관리자]
@router.get('/{branch_id}/overtime-manager/week', summary="오버타임 관리 지점별 주간 전체 조회")
async def get_branch_week_all_overtime_manager(branch_id : int, date : str, skip: int = 0, limit: int = 10, page: int = 1, overtime_manager: AsyncSession = Depends(get_db)):
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
        
        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Overtimes.application_date >= start_of_week, Overtimes.application_date <= end_of_week, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.deleted_yn == "N").order_by(Overtimes.application_date.desc()).offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 주간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 주간 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    

# 지점별 오버타임 주간 필터 전체 조회 [관리자]
@router.get('/{branch_id}/overtime-manager/week/filter', summary="오버타임 관리 지점별 주간 필터 전체 조회")
async def get_branch_week_all_overtime_manager(branch_id : int, date : str, skip: int = 0, limit: int = 10, page: int = 1, name: str = None, phone_number: str = None, branch_name: str = None, part_name: str = None, status: str = None, overtime_manager: AsyncSession = Depends(get_db)):
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


        base_query = select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Overtimes.application_date >= start_of_week, Overtimes.application_date <= end_of_week, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.deleted_yn == "N")


        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        if phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        if branch_name:
            base_query = base_query.where(Branches.name.like(f"%{branch_name}%"))
        if part_name:
            base_query = base_query.where(Parts.name.like(f"%{part_name}%"))
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))


        base_query = base_query.order_by(Overtimes.application_date.desc()).offset(skip).limit(limit)
        

        find_overtime_list = await overtime_manager.execute(base_query)
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 지점별 주간 필터 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 지점별 주간 필터 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    


""" 파트별 """

# 파트별 오버타임 관리 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager", summary= "오버타임 관리 파트별 전체 조회")
async def get_part_all_overtime_manager(branch_id : int, part_id : int, skip: int = 0, limit: int = 10, page: int = 1, overtime_manager: AsyncSession = Depends(get_db)):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.deleted_yn == "N").order_by(Overtimes.application_date.desc()).offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
        


# 파트별 오버타임 관리 필터 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager/filter", summary= "오버타임 관리 파트별 필터 전체 조회")
async def get_part_all_overtime_manager(branch_id : int, part_id : int, skip: int = 0, limit: int = 10, page: int = 1, name: str = None, phone_number: str = None, branch_name: str = None, part_name: str = None, status: str = None, overtime_manager: AsyncSession = Depends(get_db)):
    try:
        if skip == 0:
            skip = (page - 1) * limit


        base_query = select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.deleted_yn == "N")

        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        if phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        if branch_name:
            base_query = base_query.where(Branches.name.like(f"%{branch_name}%"))
        if part_name:
            base_query = base_query.where(Parts.name.like(f"%{part_name}%"))
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))


        base_query = base_query.order_by(Overtimes.application_date.desc()).offset(skip).limit(limit)

        find_overtime_list = await overtime_manager.execute(base_query)
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 필터 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 필터 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    

# 파트별 오버타임 관리 월간 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager/month", summary= "오버타임 관리 파트별 월간 전체 조회")
async def get_part_month_all_overtime_manager(branch_id : int, part_id : int, date : str, skip: int = 0, limit: int = 10, page: int = 1, overtime_manager: AsyncSession = Depends(get_db)):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)


        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= date_start_day, Overtimes.application_date <= date_end_day, Overtimes.deleted_yn == "N").order_by(Overtimes.application_date.desc()).offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 월간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 월간 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    

# 파트별 오버타임 관리 월간 필터 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager/month/filter", summary= "오버타임 관리 파트별 월간 필터 전체 조회")
async def get_part_month_all_overtime_manager(branch_id : int, part_id : int, date : str, skip: int = 0, limit: int = 10, page: int = 1, name: str = None, phone_number: str = None, branch_name: str = None, part_name: str = None, status: str = None, overtime_manager: AsyncSession = Depends(get_db)):
    try:
        if skip == 0:
            skip = (page - 1) * limit

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        base_query = select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= date_start_day, Overtimes.application_date <= date_end_day, Overtimes.deleted_yn == "N")

        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        if phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        if branch_name:
            base_query = base_query.where(Branches.name.like(f"%{branch_name}%"))
        if part_name:
            base_query = base_query.where(Parts.name.like(f"%{part_name}%"))
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))


        base_query = base_query.order_by(Overtimes.application_date.desc()).offset(skip).limit(limit)


        find_overtime_list = await overtime_manager.execute(base_query)
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 월간 필터 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 월간 필터 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    
    
# 파트별 오버타임 관리 주간 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager/week", summary= "오버타임 관리 파트별 주간 전체 조회")
async def get_part_week_all_overtime_manager(branch_id : int, part_id : int, date : str, skip: int = 0, limit: int = 10, page: int = 1, overtime_manager: AsyncSession = Depends(get_db)):
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

        find_overtime_list = await overtime_manager.execute(select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= start_of_week, Overtimes.application_date <= end_of_week, Overtimes.deleted_yn == "N").order_by(Overtimes.application_date.desc()).offset(skip).limit(limit))
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 주간 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 주간 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")
    


# 파트별 오버타임 관리 주간 필터 전체 조회 [관리자]
@router.get("/{branch_id}/parts/{part_id}/overtime-manager/week/filter", summary= "오버타임 관리 파트별 주간 필터 전체 조회")
async def get_part_week_all_overtime_manager(branch_id : int, part_id : int, date : str, skip: int = 0, limit: int = 10, page: int = 1, name: str = None, phone_number: str = None, branch_name: str = None, part_name: str = None, status: str = None, overtime_manager: AsyncSession = Depends(get_db)):
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

        base_query = select(Users, Branches, Parts, Overtimes).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).join(Overtimes, Overtimes.applicant_id == Users.id).options(load_only(Users.name), load_only(Parts.name), load_only(Branches.name), load_only(Overtimes.overtime_hours, Overtimes.status, Overtimes.application_date, Overtimes.application_memo, Overtimes.manager_id, Overtimes.manager_name, Overtimes.manager_memo)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N", Overtimes.application_date >= start_of_week, Overtimes.application_date <= end_of_week, Overtimes.deleted_yn == "N")

        
        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        if phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        if branch_name:
            base_query = base_query.where(Branches.name.like(f"%{branch_name}%"))
        if part_name:
            base_query = base_query.where(Parts.name.like(f"%{part_name}%"))
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))



        base_query = base_query.order_by(Overtimes.application_date.desc()).offset(skip).limit(limit)

        find_overtime_list = await overtime_manager.execute(base_query)
        result_overtime = find_overtime_list.fetchall()

        fetch_data = [
            {
                "user" : { "user_id" : data.Users.id, "user_name" : data.Users.name },
                "part" : { "part_id" : data.Parts.id, "part_name" : data.Parts.name },
                "branch" : { "branch_id" : data.Branches.id, "branch_name" : data.Branches.name },
                "overtime" : { "overtime_id" : data.Overtimes.id, "overtime_overtime_hours" : data.Overtimes.overtime_hours, "overtime_status" : data.Overtimes.status, "overtime_application_date" : data.Overtimes.application_date, "overtime_application_memo" : data.Overtimes.application_memo },
                "overtime_manager" : { "overtime_manager_id" : data.Overtimes.manager_id, "overtime_manager_name" : data.Overtimes.manager_name, "overtime_manager_memo" : data.Overtimes.manager_memo }
            }
            for data in result_overtime
        ]
        
        return { "message" : "성공적으로 오버타임 관리 파트별 주간 필터 전체 조회를 완료하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail=f"오버타임 관리 파트별 주간 필터 전체 조회에 오류가 발생하였습니다. Error : {str(err)}")





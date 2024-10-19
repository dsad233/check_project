from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Annotated
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.users.users_model import Users
from app.models.parts.parts_model import Parts
from app.models.commutes.commutes_model import Commutes
from app.models.branches.branches_model import Branches
from sqlalchemy.future import select
from sqlalchemy.orm import load_only
from datetime import datetime
from calendar import monthrange


router = APIRouter(dependencies=[Depends(validate_token)])
commutes_manager = async_session()


# 출근 퇴근 관리 전체 조회
@router.get('/commutes_manager')
async def get_commutes_manager(token : Annotated[Users, Depends(get_current_user)]):
    try:
        find_work_data = await commutes_manager.execute(select(Commutes).where(Commutes.user_id == Users.id, Commutes.deleted_yn == "N").order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()
        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result = find_data.fetchall() 

        formatted_data = [
            {
                "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
                "part": {"name": row.Parts.name},
                "branch": {"name": row.Branches.name},
            }
            for row in result
        ]

        return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "출근 퇴근 기록" : result_work_data}
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="출 퇴근 데이터 전체 조회에 실패하였습니다.")


""" 지점별 조회 """

# 출근 퇴근 관리 지점 월별 전체 조회
@router.get('/commutes_manager/date')
async def get_all_date_commutes_manager(date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        find_work_data = await commutes_manager.execute(select(Commutes).where(Commutes.user_id == Users.id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()
        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result = find_data.fetchall() 

        formatted_data = [
            {
                "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
                "part": {"name": row.Parts.name},
                "branch": {"name": row.Branches.name},
            }
            for row in result
        ]

        return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "출근 퇴근 기록" : result_work_data}
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="출 퇴근 데이터 전체 조회에 실패하였습니다.")
    

# 출근 퇴근 관리 지점별 조회
@router.get('/{branch_id}/commutes_manager/date')
async def get_branch_all_commutes_manager(branch_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        find_work_data = await commutes_manager.execute(select(Commutes).where(Commutes.user_id == Users.id, Users.branch_id == branch_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()
        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result = find_data.fetchall() 

        formatted_data = [
            {
                "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
                "part": {"name": row.Parts.name},
                "branch": {"name": row.Branches.name},
            }
            for row in result
        ]

        return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "출근 퇴근 기록" : result_work_data}
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="출 퇴근 데이터 전체 조회에 실패하였습니다.")
    



# 출근 퇴근 관리 지점 유저 이름별 조회
@router.get('/{branch_id}/commutes_manager/date/name')
async def get_branch_name_commutes_manager(branch_id : int, name : str, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        find_work_data = await commutes_manager.execute(select(Commutes).join(Users, Users.id == Commutes.user_id).options(load_only(Commutes.id, Commutes.clock_in, Commutes.clock_out, Commutes.work_hours)).where(Users.name.like(f"%{name}%"), Users.branch_id == branch_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()
        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.name.like(f"%{name}%"), Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result = find_data.fetchall() 

        formatted_data = [
            {
                "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
                "part": {"name": row.Parts.name},
                "branch": {"name": row.Branches.name},
            }
            for row in result
        ]

        return {"message" : "성공적으로 출근, 퇴근정보를 이름 필터 조회 하였습니다.", "data" : formatted_data, "출근 퇴근 기록" : result_work_data}
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="출 퇴근 데이터 이름으로 조회에 실패하였습니다.")


# 출근 퇴근 관리 지점 유저 전화번호 조회
@router.get('/{branch_id}/commutes_manager/date/phonenumber')
async def get_branch_phonenumber_commutes_manager(branch_id : int, phonenumber : str, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        find_work_data = await commutes_manager.execute(select(Commutes).join(Users, Users.id == Commutes.user_id).options(load_only(Commutes.id, Commutes.clock_in, Commutes.clock_out, Commutes.work_hours)).where(Users.phone_number.like(f"%{phonenumber}%"), Users.branch_id == branch_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()
        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.phone_number.like(f"%{phonenumber}%"), Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result = find_data.fetchall() 

        formatted_data = [
            {
                "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
                "part": {"name": row.Parts.name},
                "branch": {"name": row.Branches.name},
            }
            for row in result
        ]

        return {"message" : "성공적으로 출근, 퇴근 정보를 번호 조회로 하였습니다.", "data" : formatted_data, "출근 퇴근 기록" : result_work_data}
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="출 퇴근 데이터 번호로 조화에 실패하였습니다.")
    


""" 파트별 조회 """   

# 출근 퇴근 관리 파트 전체 조회
@router.get('/{branch_id}/parts/{part_id}/commutes_manager')
async def get_part_all_date_commutes_manager(branch_id : int, part_id : int, token : Annotated[Users, Depends(get_current_user)]):
    try:

        find_work_data = await commutes_manager.execute(select(Commutes).where(Commutes.user_id == Users.id, Users.branch_id == branch_id, Users.part_id == part_id, Commutes.deleted_yn == "N").order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()
        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result = find_data.fetchall() 

        formatted_data = [
            {
                "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
                "part": {"name": row.Parts.name},
                "branch": {"name": row.Branches.name},
            }
            for row in result
        ]

        return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "출근 퇴근 기록" : result_work_data}
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="출 퇴근 데이터 파트 전체 조회에 실패하였습니다.")

# 출근 퇴근 관리 파트 월별 전체 조회
@router.get('/{branch_id}/parts/{part_id}/commutes_manager/date')
async def get_part_all_date_commutes_manager(branch_id : int, part_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        find_work_data = await commutes_manager.execute(select(Commutes).where(Commutes.user_id == Users.id, Commutes.deleted_yn == "N", Users.branch_id == branch_id, Users.part_id == part_id, Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()
        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result = find_data.fetchall() 

        formatted_data = [
            {
                "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
                "part": {"name": row.Parts.name},
                "branch": {"name": row.Branches.name},
            }
            for row in result
        ]

        return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "출근 퇴근 기록" : result_work_data}
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="출 퇴근 데이터 파트 전체 조회에 실패하였습니다.")


# 출근 퇴근 관리 파트 유저 이름별 조회
@router.get('/{branch_id}/parts/{part_id}/commutes_manager/date/name')
async def get_part_name_commutes_manager(branch_id : int, part_id : int, name : str, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        find_work_data = await commutes_manager.execute(select(Commutes).join(Users, Users.id == Commutes.user_id).options(load_only(Commutes.id, Commutes.clock_in, Commutes.clock_out, Commutes.work_hours)).where(Users.name.like(f"%{name}%"), Users.branch_id == branch_id, Users.part_id == part_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()
        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.name.like(f"%{name}%"), Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result = find_data.fetchall() 

        formatted_data = [
            {
                "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
                "part": {"name": row.Parts.name},
                "branch": {"name": row.Branches.name},
            }
            for row in result
        ]

        return {"message" : "성공적으로 출근, 퇴근정보를 이름 필터 조회 하였습니다.", "data" : formatted_data, "출근 퇴근 기록" : result_work_data}
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="출 퇴근 데이터 이름으로 조회에 실패하였습니다.")



# 출근 퇴근 관리 파트 유저 전화번호 조회
@router.get('/{branch_id}/parts/{part_id}/commutes_manager/date/phonenumber')
async def get_part_phonenumber_commutes_manager(branch_id : int, part_id : int, phonenumber : str, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:

        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        find_work_data = await commutes_manager.execute(select(Commutes).join(Users, Users.id == Commutes.user_id).options(load_only(Commutes.id, Commutes.clock_in, Commutes.clock_out, Commutes.work_hours)).where(Users.phone_number.like(f"%{phonenumber}%"), Users.branch_id == branch_id, Users.part_id == part_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()
        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.phone_number.like(f"%{phonenumber}%"), Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result = find_data.fetchall() 

        formatted_data = [
            {
                "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
                "part": {"name": row.Parts.name},
                "branch": {"name": row.Branches.name},
            }
            for row in result
        ]

        return {"message" : "성공적으로 출근, 퇴근 정보를 번호 조회로 하였습니다.", "data" : formatted_data, "출근 퇴근 기록" : result_work_data}
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="출 퇴근 데이터 번호로 조화에 실패하였습니다.")
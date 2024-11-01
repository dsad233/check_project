from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middleware.tokenVerify import get_current_user, get_current_user_id, validate_token
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.overtimes_model import OvertimeSelect, OvertimeCreate, Overtimes, OvertimeUpdate, OverTime_History, ManagerMemoResponseDto

from app.models.branches.overtime_policies_model import OverTimePolicies
from app.models.users.users_model import Users
from sqlalchemy.orm import load_only
from app.enums.users import OverTimeHours

from app.common.dto.response_dto import ResponseDTO

from app.enums.users import OverTimeHours, Status
from typing import Optional
from datetime import date
from datetime import timedelta

router = APIRouter()


# 오버타임 초과 근무 생성(신청)
@router.post("", summary="오버타임 초과 근무 생성")
async def create_overtime(
    overtime: OvertimeCreate, 
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
    ):

    try:        
        # existing_overtime = await db.execute(
        #     select(Overtimes)
        #     .where(
        #         Overtimes.applicant_id == current_user_id,
        #         Overtimes.application_date == datetime.now(UTC).date(),
        #         Overtimes.overtime_hours == overtime.overtime_hours,
        #         Overtimes.deleted_yn == "N"
        #     )
        #     .limit(1)
        # )
        # if existing_overtime.scalar_one_or_none() is not None:
        #     raise HTTPException(status_code=400, detail=f"이미 오늘 {overtime.overtime_hours}분 초과근무 신청을 했습니다.")
            
        new_overtime = Overtimes(
            applicant_id=current_user_id,
            application_date = overtime.application_date,
            overtime_hours=overtime.overtime_hours,
            application_memo=overtime.application_memo,
        )

        db.add(new_overtime)
        await db.commit()
        
        return {
            "message": "초과 근무 기록이 성공적으로 생성되었습니다.",
        }
        
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error : {str(err)}")

# 오버타임 관리자 메모 상세 조회
@router.get('/manager/{id}', response_model=ResponseDTO[ManagerMemoResponseDto], summary="오버타임 관리자 메모 상세 조회")
async def get_manager(
    id : int,
    db: AsyncSession = Depends(get_db)
):
    try:
        find_manager_data = await db.execute(select(Overtimes).options(load_only(Overtimes.manager_memo)).where(Overtimes.id == id, Overtimes.deleted_yn == "N"))
        find_manager_data_result = find_manager_data.scalar_one()

        return ResponseDTO(
            status = "SUCCESS",
            message = "관리자 메모 조회가 완료되었습니다.",
            data = ManagerMemoResponseDto(
                id = find_manager_data_result.id,
                manager_memo = find_manager_data_result.manager_memo
            )
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error : {str(err)}")
    
# 오버타임 초과 근무 승인
@router.patch("/approve/{overtime_id}", summary="오버타임 승인")
async def approve_overtime(
    overtime_id: int,
    overtime_select: OvertimeSelect,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    try:
        stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N") & (Overtimes.status == "pending"))
        result = await db.execute(stmt)
        overtime = result.scalar_one_or_none()

        if overtime is None:
            raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")

        find_user = await db.execute(select(Users).where(Users.id == overtime.applicant_id, Users.deleted_yn == "N"))
        result_user = find_user.scalar_one_or_none()

        if result_user is None:
            raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")
        
        overtime.status = "approved"
        overtime.manager_id = current_user.id
        overtime.manager_name = current_user.name
        overtime.processed_date = datetime.now(UTC).date()
        overtime.is_approved = "Y"
        overtime.manager_memo = overtime_select.manager_memo

        # 기존 횟수에 대한 오버타임 조회
        find_overtime_history = await db.execute(select(OverTime_History).where(OverTime_History.user_id == result_user.id, OverTime_History.deleted_at == "N"))
        result_overtime_history = find_overtime_history.scalar_one_or_none()

        # 기존 오버타임 기록이 존재하지 않는다면 데이터 생성
        if(result_overtime_history is None):
            new_overtime_history = OverTime_History(
                user_id = result_user.id,
                ot_30_total = 0,
                ot_60_total = 0,
                ot_90_total = 0,
                ot_30_money = 0,
                ot_60_money = 0,
                ot_90_money = 0
            )

            db.add(new_overtime_history)
            await db.flush()
            await db.refresh(new_overtime_history)


            # # 해당 파트에 대한 의사 여부 확인
            find_part = await db.execute(select(Parts).where(Parts.id == result_user.part_id, Parts.deleted_yn == "N"))
            result_part = find_part.first()

            if result_part is None:
                raise HTTPException(status_code=404, detail="사용자 또는 파트 정보를 찾을 수 없습니다.")
            
            # 정책 조회
            find_overtime_policies = await db.scalars(select(OverTimePolicies).options(load_only(OverTimePolicies.doctor_ot_30, OverTimePolicies.doctor_ot_60, OverTimePolicies.doctor_ot_90, OverTimePolicies.common_ot_30, OverTimePolicies.common_ot_60, OverTimePolicies.common_ot_90)).where(result_user.branch_id == OverTimePolicies.branch_id, Branches.deleted_yn == "N", OverTimePolicies.deleted_yn == "N"))
            result_overtime_policies = find_overtime_policies.first()

            if result_overtime_policies is None:
                raise HTTPException(status_code=404, detail="오버타임 정책을 찾을 수 없습니다.")
            
            # 각 오버타임 승인 횟수에 대한 카운드 및 수당 카운트
            if(overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.THIRTY_MINUTES):
                new_overtime_history.ot_30_total +=  1
                new_overtime_history.ot_30_money += result_overtime_policies.doctor_ot_30 if result_part[0].is_doctor else result_overtime_policies.common_ot_30
            elif(overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.SIXTY_MINUTES):
                new_overtime_history.ot_60_total += 1
                new_overtime_history.ot_60_money += result_overtime_policies.doctor_ot_60 if result_part[0].is_doctor else result_overtime_policies.common_ot_60
            elif(overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.NINETY_MINUTES):
                new_overtime_history.ot_90_total += 1
                new_overtime_history.ot_90_money += result_overtime_policies.doctor_ot_90 if result_part[0].is_doctor else result_overtime_policies.common_ot_90
            await db.commit()

        else :
            # 해당 파트에 대한 의사 여부 확인
            find_part = await db.execute(select(Parts).where(Parts.id == result_user.part_id, Parts.deleted_yn == "N"))
            result_part = find_part.first()
            
            if result_part is None:
                raise HTTPException(status_code=404, detail="사용자 또는 파트 정보를 찾을 수 없습니다.")

            # 정책 조회
            find_overtime_policies = await db.scalars(select(OverTimePolicies).options(load_only(OverTimePolicies.doctor_ot_30, OverTimePolicies.doctor_ot_60, OverTimePolicies.doctor_ot_90, OverTimePolicies.common_ot_30, OverTimePolicies.common_ot_60, OverTimePolicies.common_ot_90)).where(result_user.branch_id == OverTimePolicies.branch_id, Branches.deleted_yn == "N", OverTimePolicies.deleted_yn == "N"))
            find_overtime_policies = await db.scalars(select(OverTimePolicies).join(Branches, Branches.id == OverTimePolicies.branch_id).options(load_only(OverTimePolicies.doctor_ot_30, OverTimePolicies.doctor_ot_60, OverTimePolicies.doctor_ot_90, OverTimePolicies.common_ot_30, OverTimePolicies.common_ot_60, OverTimePolicies.common_ot_90)).where(Branches.id == result_user.branch_id, result_user.branch_id == OverTimePolicies.branch_id, Branches.deleted_yn == "N", OverTimePolicies.deleted_yn == "N"))
            print(f"find_overtime_policies: {find_overtime_policies.first()}")
            result_overtime_policies = find_overtime_policies.first()

            if result_overtime_policies is None:
                raise HTTPException(status_code=404, detail="오버타임 정책을 찾을 수 없습니다.")

            # 해당 파트에 대한 의사 여부 확인
            find_part = await db.execute(select(Parts).where(Parts.id == result_user.part_id, Parts.deleted_yn == "N"))
            result_part = find_part.first()
    
            if result_part is None:
                raise HTTPException(status_code=404, detail="사용자 또는 파트 정보를 찾을 수 없습니다.")
            
            # 기존 횟수에 대한 오버타임 조회
            find_overtime_history = await db.execute(select(OverTime_History).where(OverTime_History.user_id == result_user.id, OverTime_History.deleted_at == "N"))
            result_overtime_history = find_overtime_history.scalar_one_or_none()

            if(result_overtime_history is None):
                raise HTTPException(status_code=404, detail="존재하지 않는 오버타임 히스토리 입니다.")
    
            # 각 오버타임 승인 횟수에 대한 카운드 및 수당 카운트
            if overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.THIRTY_MINUTES:
                result_overtime_history.ot_30_total += 1
                result_overtime_history.ot_30_money += result_overtime_policies.doctor_ot_30 if result_part[0].is_doctor else result_overtime_policies.common_ot_30
            elif overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.SIXTY_MINUTES:
                result_overtime_history.ot_60_total += 1
                result_overtime_history.ot_60_money += result_overtime_policies.doctor_ot_60 if result_part[0].is_doctor else result_overtime_policies.common_ot_60
            elif overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.NINETY_MINUTES:
                result_overtime_history.ot_90_total += 1
                result_overtime_history.ot_90_money += result_overtime_policies.doctor_ot_90 if result_part[0].is_doctor else result_overtime_policies.common_ot_90
    
            await db.commit()
        
        return {
            "message": "초과 근무 기록이 승인되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error {str(err)}")


# 오버타임 초과 근무 거절
@router.patch("/reject/{overtime_id}", summary="오버타임 반려")
async def reject_overtime(
    overtime_id: int,
    overtime_select: OvertimeSelect,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    try:
        stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N"))
        result = await db.execute(stmt)
        overtime = result.scalar_one_or_none()

        if overtime is None:
            raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")
        
        if (overtime != None and overtime.status == Status.REJECTED):
             raise HTTPException(status_code=400, detail="이미 거절된 오버타임 정보 입니다.")

        find_user = await db.execute(select(Users).where(Users.id == overtime.applicant_id, Users.deleted_yn == "N"))
        result_user = find_user.scalar_one_or_none()

        if result_user is None:
            raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")
        
        # 기존 오버타임 신청 목록 조회
        find_overtime_history = await db.execute(select(OverTime_History).where(OverTime_History.user_id == result_user.id, OverTime_History.deleted_at == "N"))
        result_overtime_history = find_overtime_history.scalar_one_or_none()
        
        if(result_overtime_history is None):
            overtime.status = "rejected"
            overtime.manager_id = current_user.id
            overtime.manager_name = current_user.name
            overtime.processed_date = datetime.now(UTC).date()
            overtime.is_approved = "N"
            overtime.manager_memo = overtime_select.manager_memo
            
            await db.commit()
        else:

            overtime.status = "rejected"
            overtime.manager_id = current_user.id
            overtime.manager_name = current_user.name
            overtime.processed_date = datetime.now(UTC).date()
            overtime.is_approved = "N"
            overtime.manager_memo = overtime_select.manager_memo

            # 해당 파트에 대한 의사 여부 확인
            find_part = await db.execute(select(Parts).where(Parts.id == result_user.part_id, Parts.deleted_yn == "N"))
            result_part = find_part.first()

            if result_part is None:
                raise HTTPException(status_code=404, detail="사용자 또는 파트 정보를 찾을 수 없습니다.")

            # 정책 조회
            find_overtime_policies = await db.scalars(select(OverTimePolicies).options(load_only(OverTimePolicies.doctor_ot_30, OverTimePolicies.doctor_ot_60, OverTimePolicies.doctor_ot_90, OverTimePolicies.common_ot_30, OverTimePolicies.common_ot_60, OverTimePolicies.common_ot_90)).where(result_user.branch_id == OverTimePolicies.branch_id, Branches.deleted_yn == "N", OverTimePolicies.deleted_yn == "N"))
            result_overtime_policies = find_overtime_policies.first()
            if result_overtime_policies is None:
                raise HTTPException(status_code=404, detail="오버타임 정책을 찾을 수 없습니다.")


            # 각 오버타임 승인 횟수에 대한 카운드 및 수당 카운트 
            if(overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.THIRTY_MINUTES):
                if(result_overtime_history.ot_30_total >= 1):
                    result_overtime_history.ot_30_total -= 1
                if (result_overtime_history.ot_30_money <= (result_overtime_policies.doctor_ot_30 or result_overtime_policies.common_ot_30)):
                    result_overtime_history.ot_30_money = 0
                elif(result_overtime_history.ot_30_money >= 1):
                     result_overtime_history.ot_30_money -= result_overtime_policies.doctor_ot_30 if result_part[0].is_doctor else result_overtime_policies.common_ot_30
            elif(overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.SIXTY_MINUTES):
                if(result_overtime_history.ot_60_total):
                    result_overtime_history.ot_60_total -= 1
                if (result_overtime_history.ot_60_money <= (result_overtime_policies.doctor_ot_60 or result_overtime_policies.common_ot_60)):
                    result_overtime_history.ot_60_money = 0
                elif(result_overtime_history.ot_60_money >= 1):
                    result_overtime_history.ot_60_money -= result_overtime_policies.doctor_ot_60 if result_part[0].is_doctor else result_overtime_policies.common_ot_60
            elif(overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.NINETY_MINUTES):
                if(result_overtime_history.ot_90_total >= 1):
                    result_overtime_history.ot_90_total -= 1
                if (result_overtime_history.ot_90_money <= (result_overtime_policies.doctor_ot_90 or result_overtime_policies.common_ot_90)):
                    result_overtime_history.ot_90_money = 0
                elif(result_overtime_history.ot_90_money >= 1):
                    result_overtime_history.ot_90_money -= result_overtime_policies.doctor_ot_90 if result_part[0].is_doctor else result_overtime_policies.common_ot_90
                    
            await db.commit()
        
        
        return {
            "message": "초과 근무 기록이 거절되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error {str(err)}")

# 초과 근무 목록 조회
@router.get("")
async def get_overtimes(
    date: Optional[date] = None,
    name: Optional[str] = None, 
    phone_number: Optional[str] = None, 
    branch_id: Optional[int] = None, 
    part_id: Optional[int] = None, 
    status: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    try:
        if date is None:
            date_obj = datetime.now().date()
            # weekday()가 0(월요일)~6(일요일)을 반환하므로, 
            # 일요일부터 시작하려면 현재 요일에 1을 더한 후 7로 나눈 나머지를 사용
            current_weekday = (date_obj.weekday() + 1) % 7
            date_start_day = date_obj - timedelta(days=current_weekday)
            date_end_day = date_start_day + timedelta(days=6)
        else:
            date_obj = date
            current_weekday = (date_obj.weekday() + 1) % 7
            date_start_day = date_obj - timedelta(days=current_weekday)
            date_end_day = date_start_day + timedelta(days=6)

        base_query = select(Overtimes).where(
            Overtimes.deleted_yn == "N",
            Overtimes.application_date >= date_start_day,
            Overtimes.application_date <= date_end_day
        )
        
        stmt = None

        # 사원인 경우 자신의 기록만 조회
        if current_user.role == "사원":
            base_query = base_query.where(Overtimes.applicant_id == current_user.id)

        # Users 테이블과 JOIN (검색 조건이 있는 경우)
        if name or phone_number or branch_id or part_id:
            base_query = base_query.join(Users, Overtimes.applicant_id == Users.id)

        # 이름 검색 조건
        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        # 전화번호 검색 조건
        elif phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        # 지점 검색 조건
        if branch_id:
            base_query = base_query.join(Branches, Users.branch_id == Branches.id)\
                .where(Branches.id == branch_id)
        # 파트 검색 조건
        if part_id:
            base_query = base_query.join(Parts, Users.part_id == Parts.id)\
                .where(Parts.id == part_id)
        # 상태 검색 조건
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))

        # 정렬, 페이징 적용
        skip = (page - 1) * size
        stmt = base_query.order_by(Overtimes.created_at.desc())\
            .offset(skip)\
            .limit(size)
            
        result = await db.execute(stmt)
        overtimes = result.scalars().all()
            
        formatted_data = []
        for overtime in overtimes:
            # Users, Branches, Parts 테이블 조인 쿼리
            user_query = select(Users, Branches, Parts).join(
                Branches, Users.branch_id == Branches.id
            ).join(
                Parts, Users.part_id == Parts.id
            ).where(Users.id == overtime.applicant_id)
            
            user_result = await db.execute(user_query)
            user, branch, part = user_result.first()

            overtime_data = {
                "id": overtime.id,
                "applicant_id": user.id,
                "user_name": user.name,
                "user_phone_number": user.phone_number,
                "user_gender": user.gender,
                "branch_id": branch.id,
                "branch_name": branch.name,
                "part_id": part.id,
                "part_name": part.name,
                "application_date": overtime.application_date,
                "overtime_hours": overtime.overtime_hours,
                "application_memo": overtime.application_memo,
                "manager_memo": overtime.manager_memo,
                "status": overtime.status,
                "manager_id": overtime.manager_id,
                "manager_name": overtime.manager_name,
                "processed_date": overtime.processed_date,
                "is_approved": overtime.is_approved
            }
            formatted_data.append(overtime_data)

        # 전체 레코드 수 조회
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await db.execute(count_query)
        total_count = total_count.scalar_one()

        return {
            "message": "초과 근무 기록을 정상적으로 조회하였습니다.",
            "pagination": {
                "total": total_count,
                "page": page,
                "size": size,
                "total_pages": (total_count + size - 1) // size,
            },
            "data": formatted_data,
        }
        
        
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error {str(err)}")
    
@router.get("/approved-list", summary="초과 근무 승인된 전체 조회")
async def get_overtimes_approved_list(
    current_user: Users = Depends(get_current_user), 
    date: Optional[date] = None,
    name: Optional[str] = None, 
    phone_number: Optional[str] = None, 
    branch_id: Optional[int] = None, 
    part_id: Optional[int] = None,
    is_deleted: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db)
    ):
    try:
        if date is None:
            date_obj = datetime.now().date()
            # weekday()가 0(월요일)~6(일요일)을 반환하므로, 
            # 일요일부터 시작하려면 현재 요일에 1을 더한 후 7로 나눈 나머지를 사용
            current_weekday = (date_obj.weekday() + 1) % 7
            date_start_day = date_obj - timedelta(days=current_weekday)
            date_end_day = date_start_day + timedelta(days=6)
        else:
            date_obj = date
            current_weekday = (date_obj.weekday() + 1) % 7
            date_start_day = date_obj - timedelta(days=current_weekday)
            date_end_day = date_start_day + timedelta(days=6)

        base_query = select(OverTime_History, Users, Branches, Parts).join(
            Users, OverTime_History.user_id == Users.id
        ).join(
            Branches, Users.branch_id == Branches.id
        ).join(
            Parts, Users.part_id == Parts.id
        ).where(
            OverTime_History.deleted_at == "N",
            Users.deleted_yn == "N",
            OverTime_History.created_at >= date_start_day,
            OverTime_History.created_at <= date_end_day
        )
  
        # 이름 검색 조건
        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        # 전화번호 검색 조건
        if phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        # 지점 검색 조건
        if branch_id:
            base_query = base_query.where(Branches.id == branch_id)
        # 파트 검색 조건
        if part_id:
            base_query = base_query.where(Parts.id == part_id)
        # 사용자 삭제 여부 검색 조건
        if is_deleted == "Y":
            base_query = base_query.where(Users.resignation_date != None)

        # 정렬, 페이징 적용
        skip = (page - 1) * size
        result = await db.execute(
            base_query.order_by(OverTime_History.created_at.desc())
            .offset(skip)
            .limit(size)
        )
        records = result.all()
   
        formatted_data = [{
            "id": history.id,
            "user_id": user.id,
            "user_name": user.name,
            "user_hire_date": user.hire_date,
            "user_resignation_date": user.resignation_date,
            "user_phone_number": user.phone_number,
            "branch_id": branch.id,
            "branch_name": branch.name,
            "part_id": part.id,
            "part_name": part.name,
            "ot_30_total": history.ot_30_total,
            "ot_30_money": history.ot_30_money,
            "ot_60_total": history.ot_60_total,
            "ot_60_money": history.ot_60_money,
            "ot_90_total": history.ot_90_total,
            "ot_90_money": history.ot_90_money,
            "total_count": history.ot_30_total + history.ot_60_total + history.ot_90_total,
            "total_time": history.ot_30_total * 0.5 + history.ot_60_total * 1 + history.ot_90_total * 1.5,
            "total_money": history.ot_30_money + history.ot_60_money + history.ot_90_money
        } for history, user, branch, part in records]

        # 전체 레코드 수 조회
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await db.execute(count_query)
        total_count = total_count.scalar_one()

        return {
            "message": "초과 근무 기록을 정상적으로 조회하였습니다.",
            "pagination": {
                "total": total_count,
                "page": page,
                "size": size,
                "total_pages": (total_count + size - 1) // size,
            },
            "data": formatted_data,
        }
        
        
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error {str(err)}")


# # 초과 근무 수정
# @router.patch("/{overtime_id}")
# async def update_overtime(overtime_id: int, overtime_update: OvertimeUpdate, current_user: Users = Depends(get_current_user)):
#     try:
#         stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N"))
#         result = await db.execute(stmt)
#         overtime = result.scalar_one_or_none()

#         if overtime is None:
#             raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")

#         if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자", "통합관리자"] or current_user.id != overtime.applicant_id:
#             raise HTTPException(status_code=403, detail="관리자 또는 초과 근무 신청자만 수정할 수 있습니다.")

#         if overtime.status != "pending":
#             raise HTTPException(status_code=400, detail="승인 또는 거절된 초과 근무는 수정할 수 없습니다.")

#         update_data = {}

#         # 관리자인 경우
#         if current_user.role in ["MSO 최고권한", "최고관리자", "관리자", "통합관리자"]:
#             if overtime_update.overtime_hours is not None:
#                 update_data["overtime_hours"] = overtime_update.overtime_hours
#             if overtime_update.application_memo is not None:
#                 update_data["application_memo"] = overtime_update.application_memo
#             if overtime_update.manager_memo is not None:
#                 update_data["manager_memo"] = overtime_update.manager_memo

#         # 신청자인 경우
#         elif current_user.id == overtime.applicant_id:
#             if overtime_update.application_memo is not None:
#                 update_data["application_memo"] = overtime_update.application_memo
        
#         else:
#             raise HTTPException(status_code=403, detail="초과 근무 기록을 수정할 권한이 없습니다.")

#         if not update_data:
#             raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")

#         update_stmt = update(Overtimes).where(Overtimes.id == overtime_id).values(**update_data)
#         await db.execute(update_stmt)
#         await db.commit()
        
#         return {
#             "message": "초과 근무 기록이 수정되었습니다.",
#         }
#     except HTTPException as http_err:
#         await db.rollback() 
#         raise http_err
#     except Exception as err:
#         await db.rollback()
#         print("에러가 발생하였습니다.")
#         print(err)
#         raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# # 초과 근무 삭제 (신청 취소)
# @router.delete("/{overtime_id}")
# async def delete_overtime(overtime_id: int, current_user: Users = Depends(get_current_user)):
#     try:
#         stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N") & (Overtimes.status == "pending"))
#         result = await db.execute(stmt)
#         overtime = result.scalar_one_or_none()

#         if overtime is None:
#             raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")
        
#         if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자", "통합관리자"] or current_user.id != overtime.applicant_id:
#             raise HTTPException(status_code=403, detail="관리자 또는 초과 근무 신청자만 삭제할 수 있습니다.")

#         if overtime.status != "pending":
#             raise HTTPException(status_code=400, detail="승인 또는 거절된 초과 근무는 삭제할 수 없습니다.")

#         update_stmt = update(Overtimes).where(Overtimes.id == overtime_id).values(deleted_yn="Y")
#         await db.execute(update_stmt)
#         await db.commit()
        
#         return {
#             "message": "초과 근무 기록이 삭제되었습니다.",
#         }
#     except HTTPException as http_err:
#         await db.rollback()
#         raise http_err
#     except Exception as err:
#         await db.rollback()
#         print("에러가 발생하였습니다.")
#         print(err)
#         raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
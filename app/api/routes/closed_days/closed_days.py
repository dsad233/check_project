from datetime import datetime
from typing import Annotated, List, Tuple

from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy import and_, func, select, extract
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy import and_, func, select, extract, update

from app.api.routes.closed_days.dto.closed_days_response_dto import EntireClosedDayResponseDTO, HospitalClosedDaysResponseDTO, UserClosedDayDetailDTO
from app.core.database import get_db
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.middleware.tokenVerify import get_current_user, validate_token
from app.models.closed_days.closed_days_model import ClosedDays, BranchClosedDay, UserClosedDays
from app.models.branches.work_policies_model import WorkPolicies
from app.models.users.users_model import Users
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.closed_day_service import ClosedDayService

router = APIRouter()

# 병원 월간 휴무일 조회
@router.get("/{branch_id}/closed-days/hospitals")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_all_closed_days(request : Request, branch_id : int, closed_day_service: ClosedDayService = Depends(ClosedDayService), year: int = datetime.now().year, month : int = datetime.now().month) -> HospitalClosedDaysResponseDTO:
    return HospitalClosedDaysResponseDTO.to_DTO(await closed_day_service.get_all_hospital_closed_days(branch_id, year, month)) 

# 직원 월간 휴무일 조회
@router.get("/{branch_id}/closed-days/users")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_all_user_closed_days(request : Request, branch_id : int, closed_day_service: ClosedDayService = Depends(ClosedDayService), year: int = datetime.now().year, month : int = datetime.now().month) -> List[UserClosedDayDetailDTO]:
    return await closed_day_service.get_all_user_closed_days_group_by_user_id(branch_id, year, month)
    
# 지점별 휴무일 전체(병원 + 직원) 조회 
@router.get("/{branch_id}/closed-days")
async def get_all_closed_days(request : Request, branch_id : int, service: ClosedDayService = Depends(ClosedDayService), year: int = datetime.now().year, month : int = datetime.now().month) -> EntireClosedDayResponseDTO:
    user_closed_days = await service.get_all_user_closed_days_group_by_date(branch_id, year, month)
    hospital_closed_days = await service.get_all_hospital_closed_days(branch_id, year, month)
    return EntireClosedDayResponseDTO.to_DTO(user_closed_days, hospital_closed_days)
    

# 지점 휴점일 생성 (관리자)
@router.post("/{branch_id}/closed-days", status_code=201)
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_branch_closed_day(
    request: Request,
    branch_id: int,
    closed_days: BranchClosedDay,
    db: AsyncSession = Depends(get_db),
):
    try:
        for day_item in closed_days.hospital_closed_days:
            # 기존 삭제된 데이터가 있는지 확인
            stmt = select(ClosedDays).where(
                and_(
                    ClosedDays.branch_id == branch_id,
                    ClosedDays.closed_day_date == day_item,
                    ClosedDays.user_id.is_(None),
                    ClosedDays.deleted_yn == 'Y'
                )
            )
            result = await db.execute(stmt)
            existing_closed_day = result.scalar_one_or_none()

            if existing_closed_day:
                # 기존 데이터가 있다면 복구
                existing_closed_day.deleted_yn = 'N'
                existing_closed_day.memo = "임시 휴점"
            else:
                # 새로운 데이터 생성
                new_closed_day = ClosedDays(
                    branch_id=branch_id,
                    closed_day_date=day_item,
                    memo = "임시 휴점",
                )
                db.add(new_closed_day)

        await db.commit()
        return {"message": "휴무일이 성공적으로 생성되었습니다."}
    
    except Exception as err:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(err))


# 지점 휴점일 삭제 (관리자)
@router.delete("/{branch_id}/closed-days")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_branch_closed_days(
    request: Request,
    branch_id: int,
    closed_days: BranchClosedDay,
    db: AsyncSession = Depends(get_db),
):
    try:
        dates_to_delete = closed_days.hospital_closed_days

        # 먼저 해당 레코드들이 존재하는지 확인
        stmt = select(ClosedDays.closed_day_date).where(
            and_(
                ClosedDays.branch_id == branch_id,
                ClosedDays.closed_day_date.in_(dates_to_delete),
                ClosedDays.user_id.is_(None),
                ClosedDays.deleted_yn == "N",
            )
        )
        result = await db.execute(stmt)
        existing_dates = result.scalars().all()

        if not existing_dates:
            raise HTTPException(
                status_code=404, detail="삭제할 휴무일을 찾을 수 없습니다."
            )

        # UPDATE 실행
        update_stmt = (
            update(ClosedDays)
            .where(
                and_(
                    ClosedDays.branch_id == branch_id,
                    ClosedDays.closed_day_date.in_(dates_to_delete),
                    ClosedDays.user_id.is_(None),
                    ClosedDays.deleted_yn == "N",
                )
            )
            .values(deleted_yn="Y")
        )
        await db.execute(update_stmt)
        await db.commit()

        return {"message": "휴무일이 성공적으로 삭제되었습니다."}

    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail="휴무일 삭제 중 오류가 발생했습니다."
        )

# 직원 휴무일 생성
@router.post("/{branch_id}/closed-days/employee", status_code=201)
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_employee_closed_day(
    request: Request,
    branch_id: int,
    closed_days: UserClosedDays,
    db: AsyncSession = Depends(get_db),
):
    try:
        # 모든 요청된 날짜를 하나의 리스트로 모음
        all_requested_dates = []
        for days in closed_days.user_closed_days.values():
            all_requested_dates.extend(days)
        
        # 지점 임시 휴무일 확인
        stmt = select(ClosedDays.closed_day_date).where(
            and_(
                ClosedDays.branch_id == branch_id,
                ClosedDays.closed_day_date.in_(all_requested_dates),
                ClosedDays.user_id.is_(None),  # 지점 휴무일은 user_id가 null
                ClosedDays.deleted_yn == 'N'
            )
        )
        result = await db.execute(stmt)
        branch_closed_dates = result.scalars().all()

        if branch_closed_dates:
            formatted_dates = [date.strftime('%Y-%m-%d') for date in branch_closed_dates]
            raise HTTPException(
                status_code=400,
                detail=f"다음 날짜는 지점 휴무일이므로 직원 휴무를 등록할 수 없습니다: {', '.join(formatted_dates)}"
            )
            
        # 각 유저별로 처리
        for user_id, days in closed_days.user_closed_days.items():
            # 해당 직원이 이 지점 소속인지 확인
            stmt = select(Users).where(
                and_(
                    Users.id == user_id,
                    Users.branch_id == branch_id,
                    Users.deleted_yn == 'N'
                )
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=403, 
                    detail=f"사용자 ID {user_id}는 해당 지점의 직원이 아닙니다."
                )

            for day_item in days:
                # 기존 삭제된 데이터 확인
                stmt = select(ClosedDays).where(
                    and_(
                        ClosedDays.branch_id == branch_id,
                        ClosedDays.closed_day_date == day_item,
                        ClosedDays.user_id == user_id,
                        ClosedDays.deleted_yn == 'Y'
                    )
                )
                result = await db.execute(stmt)
                existing_closed_day = result.scalar_one_or_none()

                if existing_closed_day:
                    # 기존 데이터 복구
                    existing_closed_day.deleted_yn = 'N'
                    existing_closed_day.memo = "직원 휴무"
                else:
                    # 새로운 데이터 생성
                    new_closed_day = ClosedDays(
                        branch_id=branch_id,
                        user_id=user_id,
                        closed_day_date=day_item,
                        memo="직원 휴무",
                    )
                    db.add(new_closed_day)

        await db.commit()
        return {"message": "직원 휴무일이 성공적으로 생성되었습니다."}
    
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(err))

# 직원 휴무일 삭제
@router.delete("/{branch_id}/closed-days/employee")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_employee_closed_days(
    request: Request,
    branch_id: int,
    closed_days: UserClosedDays,
    db: AsyncSession = Depends(get_db),
):
    try:
        for user_id, dates_to_delete in closed_days.user_closed_days.items():
            # 해당 직원이 이 지점 소속인지 확인
            stmt = select(Users).where(
                and_(
                    Users.id == user_id,
                    Users.branch_id == branch_id,
                    Users.deleted_yn == 'N'
                )
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=403, 
                    detail=f"사용자 ID {user_id}는 해당 지점의 직원이 아닙니다."
                )

            # 삭제할 레코드 확인
            stmt = select(ClosedDays.closed_day_date).where(
                and_(
                    ClosedDays.branch_id == branch_id,
                    ClosedDays.closed_day_date.in_(dates_to_delete),
                    ClosedDays.user_id == user_id,
                    ClosedDays.deleted_yn == "N",
                )
            )
            result = await db.execute(stmt)
            existing_dates = result.scalars().all()

            if not existing_dates:
                raise HTTPException(
                    status_code=404, 
                    detail=f"사용자 ID {user_id}의 삭제할 휴무일을 찾을 수 없습니다."
                )

            # UPDATE 실행
            update_stmt = (
                update(ClosedDays)
                .where(
                    and_(
                        ClosedDays.branch_id == branch_id,
                        ClosedDays.closed_day_date.in_(dates_to_delete),
                        ClosedDays.user_id == user_id,
                        ClosedDays.deleted_yn == "N",
                    )
                )
                .values(deleted_yn="Y")
            )
            await db.execute(update_stmt)

        await db.commit()
        return {"message": "직원 휴무일이 성공적으로 삭제되었습니다."}

    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        raise HTTPException(status_code=500, detail="직원 휴무일 삭제 중 오류가 발생했습니다.")
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Request
from sqlalchemy import select, func, update
from datetime import UTC, datetime, date, timedelta
from typing import Optional
from decimal import Decimal

from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.core.permissions.auth_utils import available_higher_than
from app.middleware.tokenVerify import get_current_user_id, get_current_user
from app.models.users.leave_histories_model import LeaveHistories, LeaveHistoriesCreate, LeaveHistoriesSearchDto, LeaveHistoriesApprove, LeaveHistoriesUpdate
from app.models.branches.user_leaves_days import UserLeavesDays, UserLeavesDaysResponse
from app.models.users.users_model import Users
from app.enums.users import Role, Status
from app.models.parts.parts_model import Parts
from app.models.branches.branches_model import Branches
from app.models.branches.leave_categories_model import LeaveCategory
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import user_service

router = APIRouter()
# db = async_session()

# 현재 사용자의 연차 일수 정보 조회
@router.get("/leave-histories/current-user-leaves", response_model=UserLeavesDaysResponse, summary="현재 사용자의 연차 일수 정보 조회", description="현재 사용자의 연차 일수 정보를 조회합니다.")
async def get_current_user_leaves(
    *,
    branch_id: int = Query(..., description="지점 ID를 입력합니다."),
    year: Optional[int] = Query(None, description="연도를 입력합니다. 예) 2024"),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        if year is None:
            year = date.today().year
            
        # 해당 연도의 시작일과 종료일 설정
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        # 모든 기록 조회
        leave_query = select(UserLeavesDays).where(
            UserLeavesDays.user_id == current_user_id,
            UserLeavesDays.branch_id == branch_id,
            UserLeavesDays.deleted_yn == 'N',
            UserLeavesDays.created_at >= start_date,
            UserLeavesDays.created_at <= end_date
        ).order_by(UserLeavesDays.created_at.desc())
        
        result = await db.execute(leave_query)
        leave_info = result.scalar_one_or_none()
        
        if not leave_info:
            return {
                "user_id": current_user_id,
                "branch_id": branch_id,
                "year": year,
                "increased_days": 0.0,
                "decreased_days": 0.0,
                "total_leave_days": 0.0,
                "message": f"{year}년도의 연차 정보가 없습니다."
            }
            
        # 모든 increased_days 합산
        total_increased = float(leave_info.increased_days) if leave_info.increased_days is not None else 0.0
        total_decreased = float(leave_info.decreased_days) if leave_info.decreased_days is not None else 0.0

        return UserLeavesDaysResponse(
            user_id=current_user_id,
            branch_id=branch_id,
            year=year,
            increased_days=total_increased,
            decreased_days=total_decreased,
            total_leave_days=total_increased - total_decreased
        )
        
        
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

@router.get("/leave-histories", summary="연차 신청 목록 조회", description="연차 신청 목록을 조회합니다.")
async def get_leave_histories(
    search: LeaveHistoriesSearchDto = Depends(), # 검색 조건
    date: Optional[date] = Query(None, description="시작일 계산을 위한 날짜를 입력합니다. 공백인 경우 오늘을 포함한 주의 일요일-토요일 기간을 조회합니다. 예) YYYY-MM-DD"), # 시작일 계산을 위한 날짜 입력
    branch_id: Optional[int] = Query(None, description="검색할 지점 ID를 입력합니다. 공백인 경우 전체 조회합니다."), # 지점
    part_id: Optional[str] = Query(None, description="검색할 파트 ID를 입력합니다. 공백인 경우 전체 조회합니다."), # 파트
    search_name: Optional[str] = Query(None, description="검색할 이름을 입력합니다. 공백인 경우 전체 조회합니다."), # 이름
    search_phone: Optional[str] = Query(None, description="검색할 전화번호를 입력합니다. 공백인 경우 전체 조회합니다."), # 전화번호
    page: int = Query(1, gt=0, description="페이지 번호를 입력합니다. 기본값은 1입니다."),
    size: int = Query(10, gt=0, description="페이지당 레코드 수를 입력합니다. 기본값은 10입니다."),
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자", "통합관리자", "사원"]:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        if date is None:
            # 날짜가 없으면 현재 날짜 기준으로 해당 주의 일요일-토요일
            date_obj = datetime.now().date()    
            current_weekday = date_obj.weekday()
            # 현재 날짜에서 현재 요일만큼 빼서 일요일을 구함
            date_start_day = date_obj - timedelta(days=current_weekday)
            # 일요일부터 6일을 더해서 토요일을 구함
            date_end_day = date_start_day + timedelta(days=6)
        else:
            date_obj = date
            current_weekday = date_obj.weekday()
            date_start_day = date_obj - timedelta(days=current_weekday)
            date_end_day = date_start_day + timedelta(days=6)
        
        base_query = select(LeaveHistories).where(
            LeaveHistories.deleted_yn == 'N',
            LeaveHistories.application_date >= date_start_day,
            LeaveHistories.application_date <= date_end_day,
        )
        
        if base_query is None:
            raise HTTPException(status_code=404, detail="연차 신청 목록을 찾을 수 없습니다.")
        
        stmt = None

        # 필터 적용 부분 수정
        if branch_id:   
            base_query = base_query.join(Branches, LeaveHistories.branch_id == Branches.id)\
                .where(Branches.id == branch_id)
        if part_id:
            base_query = base_query.join(Parts, LeaveHistories.part_id == Parts.id)\
                .where(Parts.id == part_id)
        if search_name:
            base_query = base_query.join(Users)\
                .where(Users.name.ilike(f"%{search_name}%"))
        if search_phone:
            base_query = base_query.join(Users)\
                .where(Users.phone_number.ilike(f"%{search_phone}%"))
        if search.kind:
            base_query = base_query.join(LeaveHistories.leave_category)\
                .where(LeaveCategory.name.ilike(f"%{search.kind}%"))
        if search.status:
            base_query = base_query.where(LeaveHistories.status.ilike(f"%{search.status}%"))
        
        skip = (page - 1) * size
        stmt = base_query.order_by(LeaveHistories.created_at.desc())\
            .offset(skip)\
            .limit(size)
            
        result = await db.execute(stmt)
        leave_histories = result.scalars().all()
        
        formatted_data = []
        for leave_history in leave_histories:
            user_query = select(Users, Branches, Parts).join(
            Branches, Users.branch_id == Branches.id
            ).join(
                Parts, Users.part_id == Parts.id
            ).where(Users.id == leave_history.user_id)
            
            user_result = await db.execute(user_query)
            user, branch, part = user_result.first()

            category_query = select(LeaveCategory).where(
                LeaveCategory.id == leave_history.leave_category_id
            )
            category_result = await db.execute(category_query)
            leave_category = category_result.scalar_one_or_none()
            
            leave_history_data = {
                "id": leave_history.id,
                "search_branch_id": branch.id,
                "branch_name": branch.name,
                "user_id": user.id,
                "user_name": user.name,
                "part_id": part.id,
                "part_name": part.name,
                "application_date": leave_history.application_date,
                "start_date": leave_history.start_date,
                "end_date": leave_history.end_date,
                "leave_category_id": leave_history.leave_category_id,
                "leave_category_name": leave_category.name,
                "decreased_days": float(leave_history.decreased_days) if leave_history.decreased_days is not None else 0.0,
                "status": leave_history.status,
                "applicant_description": leave_history.applicant_description,
                "manager_id": leave_history.manager_id,
                "manager_name": leave_history.manager_name,
                "admin_description": leave_history.admin_description,
                "approve_date": leave_history.approve_date
            }
            formatted_data.append(leave_history_data)
            
        # 전체 레코드 수 계산
        count_query = base_query.with_only_columns(func.count())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar_one()
            
        return {
            "list": formatted_data,
            "pagination": {
                "total": total_count,
                "page": page,
                "size": size,
                "total_pages": (total_count + size - 1) // size
            },
            "message": "연차 신청 목록을 정상적으로 조회하였습니다."
        }
        
    except Exception as err:
        print(f"에러가 발생하였습니다: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@router.get("/leave-histories/approve", summary="연차 전체 승인 목록 조회", description="연차 전체 승인 목록을 조회합니다.")
@available_higher_than(Role.ADMIN)
async def get_approve_leave(
    context: Request,
    search: LeaveHistoriesSearchDto = Depends(), # 검색 조건
    date: Optional[date] = Query(None, description="시작일 계산을 위한 날짜를 입력합니다. 공백인 경우 오늘을 포함한 주의 일요일-토요일 기간을 조회합니다. 예) YYYY-MM-DD"), # 시작일
    branch_id: Optional[int] = Query(None, description="검색할 지점 ID를 입력합니다. 공백인 경우 전체 조회합니다."), # 지점
    part_id: Optional[str] = Query(None, description="검색할 파트 ID를 입력합니다. 공백인 경우 전체 조회합니다."), # 파트
    search_name: Optional[str] = Query(None, description="검색할 이름을 입력합니다. 공백인 경우 전체 조회합니다."), # 이름
    search_phone: Optional[str] = Query(None, description="검색할 전화번호를 입력합니다. 공백인 경우 전체 조회합니다."), # 전화번호
    page: int = Query(1, gt=0, description="페이지 번호를 입력합니다. 기본값은 1입니다."),
    size: int = Query(10, gt=0, description="페이지당 레코드 수를 입력합니다. 기본값은 10입니다."),
    current_user: Users = Depends(get_current_user),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자", "통합관리자", "사원"]:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        if date is None:
            # 날짜가 없으면 현재 날짜 기준으로 해당 주의 일요일-토요일
            date_obj = datetime.now().date()    
            current_weekday = date_obj.weekday()
            # 현재 날짜에서 현재 요일만큼 빼서 일요일을 구함
            date_start_day = date_obj - timedelta(days=current_weekday)
            # 일요일부터 6일을 더해서 토요일을 구함
            date_end_day = date_start_day + timedelta(days=6)
        else:
            date_obj = date
            current_weekday = date_obj.weekday()
            date_start_day = date_obj - timedelta(days=current_weekday)
            date_end_day = date_start_day + timedelta(days=6)
        
        base_query = select(LeaveHistories).where(
            LeaveHistories.deleted_yn == 'N',
            LeaveHistories.application_date >= date_start_day,
            LeaveHistories.application_date <= date_end_day,
            LeaveHistories.status == Status.APPROVED
        )
        
        if base_query is None:
            raise HTTPException(status_code=404, detail="연차 신청 목록을 찾을 수 없습니다.")
        
        stmt = None

        # 필터 적용 부분 수정
        if branch_id:   
            base_query = base_query.join(Branches, LeaveHistories.branch_id == Branches.id)\
                .where(Branches.id == branch_id)
        if part_id:
            base_query = base_query.join(Parts, LeaveHistories.part_id == Parts.id)\
                .where(Parts.id == part_id)
        if search_name:
            base_query = base_query.join(Users)\
                .where(Users.name.ilike(f"%{search_name}%"))
        if search_phone:
            base_query = base_query.join(Users)\
                .where(Users.phone_number.ilike(f"%{search_phone}%"))
        if search.kind:
            base_query = base_query.join(LeaveHistories.leave_category)\
                .where(LeaveCategory.name.ilike(f"%{search.kind}%"))
        if search.status:
            base_query = base_query.where(LeaveHistories.status.ilike(f"%{search.status}%"))
        
        skip = (page - 1) * size
        stmt = base_query.order_by(LeaveHistories.created_at.desc())\
            .offset(skip)\
            .limit(size)
            
        result = await db.execute(stmt)
        leave_histories = result.scalars().all()
        
        formatted_data = []
        for leave_history in leave_histories:
            user_query = select(Users, Branches, Parts).join(
            Branches, Users.branch_id == Branches.id
            ).join(
                Parts, Users.part_id == Parts.id
            ).where(Users.id == leave_history.user_id)
            
            user_result = await db.execute(user_query)
            user, branch, part = user_result.first()

            category_query = select(LeaveCategory).where(
                LeaveCategory.id == leave_history.leave_category_id
            )
            category_result = await db.execute(category_query)
            leave_category = category_result.scalar_one_or_none()
            
            leave_history_data = {
                "id": leave_history.id,
                "search_branch_id": branch.id,
                "branch_name": branch.name,
                "user_id": user.id,
                "user_name": user.name,
                "part_id": part.id,
                "part_name": part.name,
                "application_date": leave_history.application_date,
                "start_date": leave_history.start_date,
                "end_date": leave_history.end_date,
                "leave_category_id": leave_history.leave_category_id,
                "leave_category_name": leave_category.name,
                "decreased_days": float(leave_history.decreased_days) if leave_history.decreased_days is not None else 0.0,
                "status": leave_history.status,
                "applicant_description": leave_history.applicant_description,
                "manager_id": leave_history.manager_id,
                "manager_name": leave_history.manager_name,
                "admin_description": leave_history.admin_description,
                "approve_date": leave_history.approve_date
            }
            formatted_data.append(leave_history_data)
            
        # 전체 레코드 수 계산
        count_query = base_query.with_only_columns(func.count())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar_one()
            
        return {
            "list": formatted_data,
            "pagination": {
                "total": total_count,
                "page": page,
                "size": size,
                "total_pages": (total_count + size - 1) // size
            },
            "message": "연차 승인 내역 목록을 정상적으로 조회하였습니다."
        }
        
    except Exception as err:
        print(f"에러가 발생하였습니다: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    
@router.post("/leave-histories", summary="연차 신청", description="연차를 신청합니다.")
async def create_leave_history(
    context: Request,
    leave_create: LeaveHistoriesCreate,
    branch_id: int = Query(..., description="현재 사용자가 포함된 지점 ID를 입력합니다."),
    decreased_days: float = Query(..., description="사용할 연차 일수를 입력합니다. 타입은 float입니다. 예) 1.0"),
    start_date: date = Query(..., description="시작일을 입력합니다. 예) YYYY-MM-DD"),
    end_date: date = Query(..., description="종료일을 입력합니다. 예) YYYY-MM-DD"),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")
        
        # 사용 가능한 연차 일수 체크
        user = await user_service.get_branch_users_leave(request=BaseSearchDto(record_size=1), session=db, branch_id=branch_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        if user.data[0].total_leave_days < decreased_days:
            raise HTTPException(status_code=400, detail="사용 가능한 연차 일수가 부족합니다.")
        
        # LeaveHistories 생성 및 flush
        create = LeaveHistories(
            branch_id=branch_id,
            part_id=current_user.part_id,
            user_id=current_user_id,
            leave_category_id=leave_create.leave_category_id,
            decreased_days=decreased_days,
            start_date=start_date,
            end_date=end_date,
            application_date=datetime.now().date(),
            applicant_description=leave_create.applicant_description or None,
            status=Status.PENDING
        )
        db.add(create)
        await db.flush()
        await db.refresh(create)
        
        # ID 값을 미리 저장
        leave_history_id = create.id
        
        # UserLeavesDays 조회
        leave_history_query = select(UserLeavesDays)\
            .where(
                UserLeavesDays.user_id == current_user_id,
                UserLeavesDays.deleted_yn == 'N'
            )
        
        leave_history_result = await db.execute(leave_history_query)
        user_leaves_days_record = leave_history_result.scalar_one_or_none()

        if user_leaves_days_record is None:
            user_leaves_days = UserLeavesDays(
                user_id=current_user_id,
                increased_days=0.00,
                decreased_days=0.00,
                total_leave_days=0.00,
                deleted_yn='N'
            )
            db.add(user_leaves_days)
            await db.flush()
        
        await db.commit()
            
        return {
            "message": "연차 생성에 성공하였습니다.",
            "leave_history_id": leave_history_id
        }
            
    except Exception as err:
        await db.rollback()
        print(f"연차 생성 중 오류 발생: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@router.patch('/{branch_id}/leave-histories/{leave_id}/approve', summary="연차 승인/반려", description="연차를 승인/반려합니다.")
async def approve_leave(
    leave_approve: LeaveHistoriesApprove,
    leave_id: int = Path(..., description="승인/반려 결정을 할 연차 ID를 입력합니다."),
    branch_id: int = Path(..., description="현재 사용자가 포함된 지점 ID를 입력합니다."),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == "N")
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()
        
        if current_user.role.strip() == "MSO 관리자":
            pass
        
        query = select(LeaveHistories).where(LeaveHistories.id == leave_id, LeaveHistories.branch_id == branch_id, LeaveHistories.deleted_yn == "N")
        result = await db.execute(query)
        leave_history = result.scalar_one_or_none()
        
        if not leave_history:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")
        
        now = datetime.now(UTC).date()
        if leave_history.start_date >= now:
            leave_history.status = leave_approve.status
            leave_history.admin_description = leave_approve.admin_description
            leave_history.approve_date = datetime.now()
            
            if leave_approve.status == Status.APPROVED:
                decreased_days = Decimal(str(leave_history.decreased_days))
                await db.execute(
                    update(Users)
                    .where(Users.id == leave_history.user_id)
                    .values(
                        total_leave_days=Users.total_leave_days - decreased_days,
                        updated_at=datetime.now(UTC)
                    )
                )
            if leave_history.status == Status.APPROVED:
                existing_leave_days = await db.execute(
                    select(UserLeavesDays)
                    .where(
                        UserLeavesDays.user_id == leave_history.user_id,
                        UserLeavesDays.deleted_yn == 'N'
                    )
                    .order_by(UserLeavesDays.created_at.desc())
                )
                leave_days_record = existing_leave_days.scalar_one_or_none()
                
                if not leave_days_record:
                    raise HTTPException(status_code=404, detail="사용자의 연차 정보를 찾을 수 없습니다.")
                
                if leave_days_record.total_leave_days < leave_history.decreased_days:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"승인 불가: 신청 일수({leave_history.decreased_days}일)가 남은 연차 일수({leave_days_record.total_leave_days}일)보다 많습니다."
                    )

                # UserLeavesDays 업데이트
                leave_days_record.decreased_days += decreased_days
                leave_days_record.total_leave_days -= decreased_days
                leave_days_record.updated_at = datetime.now(UTC)
                
                # Users 업데이트
                await db.execute(
                    update(Users)
                    .where(Users.id == leave_history.user_id)
                    .values(total_leave_days=Users.total_leave_days - decreased_days, updated_at=datetime.now(UTC))
                )

                # LeaveHistories 업데이트
                leave_history.status = Status.APPROVED
                leave_history.decreased_days += decreased_days
                leave_history.manager_id = current_user.id
                leave_history.manager_name = current_user.name
                leave_history.approve_date = datetime.now(UTC)
                leave_history.admin_description = leave_approve.admin_description
                leave_history.updated_at = datetime.now(UTC)
                message = "연차 승인에 성공하였습니다."
                
            else:  # Status.REJECTED
                leave_history.status = Status.REJECTED
                leave_history.manager_id = current_user.id
                leave_history.manager_name = current_user.name
                leave_history.approve_date = datetime.now(UTC)
                leave_history.admin_description = leave_approve.admin_description
                leave_history.updated_at = datetime.now(UTC)
                message = "연차 반려에 성공하였습니다."
                
            await db.commit()
            return {"message": message}
        else:
            raise HTTPException(status_code=400, detail="날짜가 지났습니다.")
            
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

@router.patch("/leave-histories/{leave_id}", summary="연차 수정", description="연차를 수정합니다.")
async def update_leave(
    leave_update: LeaveHistoriesUpdate,
    branch_id: int = Query(..., description="현재 사용자가 포함된 지점 ID를 입력합니다."),
    leave_id: int = Path(..., description="수정할 연차 ID를 입력합니다."),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")

        query = select(LeaveHistories).where(LeaveHistories.id == leave_id, LeaveHistories.branch_id == branch_id, LeaveHistories.deleted_yn == 'N')
        result = await db.execute(query)
        leave_history = result.scalar_one_or_none()

        if not leave_history:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

        is_admin = current_user.role.strip() in ["MSO 최고권한", "최고관리자", "통합관리자"]

        if leave_history.user_id != current_user.id and not is_admin:
            raise HTTPException(status_code=403, detail="연차를 수정할 권한이 없습니다.")

        if leave_update.leave_category_id:
            leave_history.leave_category_id = leave_update.leave_category_id
        if leave_update.date:
            leave_history.application_date = leave_update.date
        if leave_update.applicant_description:
            leave_history.applicant_description = leave_update.applicant_description
            
        await db.commit()
        return {"message": "연차 수정에 성공하였습니다."}
        
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

@router.delete("/leave-histories/{leave_id}", summary="연차 삭제", description="연차를 삭제합니다.")
async def delete_leave(
    branch_id: int = Query(..., description="현재 사용자가 포함된 지점 ID를 입력합니다."),
    leave_id: int = Path(..., description="삭제할 연차 ID를 입력합니다."),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")

        query = select(LeaveHistories).where(LeaveHistories.id == leave_id, LeaveHistories.branch_id == branch_id, LeaveHistories.deleted_yn == 'N')
        result = await db.execute(query)
        leave_history = result.scalar_one_or_none()

        if not leave_history:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

        if leave_history.request_user_id != current_user.id and current_user.role.strip() not in ["MSO 최고권한", "최고관리자", "통합관리자"]:
            raise HTTPException(
                status_code=403, detail="연차를 삭제할 권한이 없습니다."
            )

        if leave_history.status.strip() != "확인중":
            raise HTTPException(
                status_code=400, detail="승인/반려된 연차는 삭제할 수 없습니다."
            )

        leave_history.deleted_yn = "Y"
        await db.commit()
        return {"message": "연차 삭제에 성공하였습니다."}
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

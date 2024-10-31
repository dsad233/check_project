from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy import select, func
from datetime import datetime, date, timedelta
from typing import Optional

from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.middleware.tokenVerify import validate_token, get_current_user_id, get_current_user
from app.models.users.leave_histories_model import LeaveHistories, LeaveHistoriesCreate, LeaveHistoriesSearchDto, LeaveHistoriesApprove, LeaveHistoriesUpdate
from app.models.branches.user_leaves_days import UserLeavesDays, UserLeavesDaysResponse
from app.models.users.users_model import Users
from app.enums.users import Status
from app.models.parts.parts_model import Parts
from app.models.branches.branches_model import Branches
from app.models.branches.leave_categories_model import LeaveCategory
from sqlalchemy.ext.asyncio import AsyncSession

from app.service import user_service

router = APIRouter(dependencies=[Depends(validate_token)])
# db = async_session()

# 현재 사용자의 연차 일수 정보 조회
@router.get("/current-user-leaves", response_model=UserLeavesDaysResponse, summary="현재 사용자의 연차 일수 정보 조회", description="현재 사용자의 연차 일수 정보를 조회합니다.")
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

        # 모든 기록 조회
        leave_query = select(UserLeavesDays).where(
            UserLeavesDays.user_id == current_user_id,
            UserLeavesDays.branch_id == branch_id,
            UserLeavesDays.deleted_yn == 'N',
            func.extract('year', UserLeavesDays.created_at) == year 
        ).order_by(UserLeavesDays.created_at.desc())
        
        result = await db.execute(leave_query)
        leave_info = result.scalars().all()

        if not leave_info:
            raise HTTPException(status_code=404, detail="해당 연도의 연차 정보를 찾을 수 없습니다.")
        
        # 가장 최근 레코드 사용
        latest_info = leave_info[0]

        # 모든 increased_days 합산
        total_increased = float(latest_info.total_increased_days) if latest_info.total_increased_days is not None else 0.0
        total_decreased = float(latest_info.total_decreased_days) if latest_info.total_decreased_days is not None else 0.0

        return UserLeavesDaysResponse(
            user_id=current_user_id,
            branch_id=branch_id, 
            year=year,
            increased_days=total_increased,  # 합산된 증가 일수
            decreased_days=total_decreased,  # 합산된 감소 일수
            total_leave_days=100 + total_increased - total_decreased,  # 사용 가능한 연차 일수
            leave_category_id=latest_info.leave_category_id
        )

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

@router.get("/list", summary="연차 신청 목록 조회", description="연차 신청 목록을 조회합니다.")
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
            LeaveHistories.application_date <= date_end_day
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
            
            leave_history_data = {
                "id": leave_history.id,
                "branch_id": branch.id,
                "branch_name": branch.name,
                "user_id": user.id,
                "user_name": user.name,
                "part_id": part.id,
                "part_name": part.name,
                "application_date": leave_history.application_date,
                "start_date": leave_history.start_date,
                "end_date": leave_history.end_date,
                "leave_category_id": leave_history.leave_category_id,
                "decreased_days": float(leave_history.decreased_days) if leave_history.decreased_days is not None else 0.0,
                "status": leave_history.status,
                "applicant_description": leave_history.applicant_description,
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

@router.get("/approve-list", summary="연차 전체 승인 목록 조회", description="연차 전체 승인 목록을 조회합니다.")
async def get_approve_leave(
    search: LeaveHistoriesSearchDto = Depends(), # 검색 조건
    date: Optional[date] = Query(None, description="시작일 계산을 위한 날짜를 입력합니다. 공백인 경우 오늘을 포함한 주의 일요일-토요일 기간을 조회합니다. 예) YYYY-MM-DD"), # 시작일
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
            LeaveHistories.status == 'approved'
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
            
            leave_history_data = {
                "id": leave_history.id,
                "branch_id": branch.id,
                "branch_name": branch.name,
                "user_id": user.id,
                "user_name": user.name,
                "part_id": part.id,
                "part_name": part.name,
                "application_date": leave_history.application_date,
                "start_date": leave_history.start_date,
                "end_date": leave_history.end_date,
                "leave_category_id": leave_history.leave_category_id,
                "decreased_days": float(leave_history.decreased_days) if leave_history.decreased_days is not None else 0.0,
                "status": leave_history.status,
                "applicant_description": leave_history.applicant_description,
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

@router.post("", summary="연차 신청", description="연차를 신청합니다.")
async def create_leave_history(
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
        
        existing_query = select(LeaveHistories).where(
            LeaveHistories.user_id == current_user_id,
            LeaveHistories.application_date == datetime.now().date(),
            LeaveHistories.deleted_yn == 'N',
            LeaveHistories.status != Status.REJECTED
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="이미 오늘 연차를 신청하셨습니다. 다음날에 다시 신청해주세요.")
        
        # 현재 연도의 total_decreased_days 계산
        # current_year = datetime.now().year
        # total_query = select(func.sum(UserLeavesDays.decreased_days)).where(
        #     UserLeavesDays.user_id == current_user.id,
        #     UserLeavesDays.branch_id == branch_id,
        #     UserLeavesDays.deleted_yn == 'N',
        #     func.extract('year', UserLeavesDays.created_at) == current_year
        # )
        # total_result = await db.execute(total_query)
        # current_total = total_result.scalar() or 0.0
        
        # 새로운 total_decreased_days 계산
        # new_total_decreased = float(current_total) + decreased_days
        
        # 사용 가능한 연차 일수 체크
        user = await user_service.get_branch_users_leave(session=db, branch_id=branch_id, search=BaseSearchDto(record_size=1))
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        if user.data[0].total_leave_days < decreased_days:
            raise HTTPException(status_code=400, detail="사용 가능한 연차 일수가 부족합니다.")
        else:
            create = LeaveHistories(
                branch_id=branch_id,
                user_id=current_user.id,
                leave_category_id=leave_create.leave_category_id,
                decreased_days=decreased_days,
                start_date=start_date,
                end_date=end_date,
                application_date=datetime.now().date(),
                applicant_description=leave_create.applicant_description or None,
                status = Status.PENDING
            )
            db.add(create)
            
        
        await db.flush()
        leave_history = select(UserLeavesDays)\
            .where(UserLeavesDays.user_id == current_user.id, UserLeavesDays.branch_id == branch_id, UserLeavesDays.deleted_yn == 'N')
        
        leave_history_result = await db.execute(leave_history)
        user_leaves_days_record = leave_history_result.scalar_one_or_none()
        
        print(f"existing_record: {user_leaves_days_record}")

        # 레코드가 없는 경우에만 새로 생성
        if user_leaves_days_record is None:
            user_leaves_days = UserLeavesDays(
                user_id=current_user.id,
                branch_id=branch_id,
                leave_category_id=leave_create.leave_category_id,
                leave_history_id=create.id,
                increased_days=0.00,
                total_increased_days=0.00,
                decreased_days=0.00,
                total_decreased_days=0.00,
                total_leave_days=user.data[0].total_leave_days,
                description=leave_create.applicant_description,
                is_paid=True,
                is_approved=False,
                deleted_yn='N'
            )
            db.add(user_leaves_days)
            print(f"user_leaves_days: {user_leaves_days.user_id}")
        
        await db.commit()
        return {"message": "연차 생성에 성공하였습니다."}
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.patch("/{leave_id}/approve", summary="연차 승인/반려", description="연차를 승인/반려합니다.")
async def approve_leave(
    leave_approve: LeaveHistoriesApprove,
    leave_id: int = Path(..., description="승인/반려 결정을 할 연차 ID를 입력합니다."),
    branch_id: int = Query(..., description="현재 사용자가 포함된 지점 ID를 입력합니다."),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.role.strip() == "사원":
            raise HTTPException(status_code=403, detail="사원은 연차를 승인할 수 없습니다.")
        elif current_user.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")

        query = select(LeaveHistories).where(LeaveHistories.id == leave_id, LeaveHistories.branch_id == branch_id, LeaveHistories.deleted_yn == 'N')
        result = await db.execute(query)
        leave_history = result.scalar_one_or_none()

        if not leave_history:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

        now = datetime.now().date()
        
        if leave_history.application_date >= now:
            leave_history.status = leave_approve.status
            leave_history.admin_description = leave_approve.admin_description or None
            leave_history.approve_date = datetime.now()
            
            if leave_approve.status == Status.APPROVED:
                await user_service.minus_total_leave_days(
                    session=db, 
                    user_id=leave_history.user_id, 
                    count=int(leave_history.decreased_days)
                )
            user = await user_service.get_branch_users_leave(session=db, branch_id=branch_id, search=BaseSearchDto(record_size=1))
            if not user:
                raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
            
        if leave_history.status == Status.APPROVED:
            leave_days_query = select(UserLeavesDays).where(
                UserLeavesDays.user_id == leave_history.user_id,
                UserLeavesDays.branch_id == branch_id,
                UserLeavesDays.deleted_yn == 'N'
            ).order_by(UserLeavesDays.created_at.desc())
            
            result = await db.execute(leave_days_query)
            latest_record = result.scalar_one_or_none()
            
            if latest_record:
                # 새로운 레코드 생성
                new_total_decreased = float(latest_record.total_decreased_days or 0) + float(leave_history.decreased_days)
                new_total_leave = float(latest_record.total_leave_days or 0) - float(leave_history.decreased_days)
                
                new_record = UserLeavesDays(
                    user_id=leave_history.user_id,
                    branch_id=branch_id,
                    leave_category_id=leave_history.leave_category_id,
                    leave_history_id=leave_history.id,
                    increased_days=0.00,
                    total_increased_days=latest_record.total_increased_days,
                    decreased_days=float(leave_history.decreased_days),
                    total_decreased_days=new_total_decreased,
                    total_leave_days=new_total_leave,
                    description=leave_approve.admin_description,
                    is_paid=True,
                    is_approved=True,
                    deleted_yn='N'
                )
                db.add(new_record)
            
            await db.commit()
            return {
                "message": "연차 승인/반려에 성공하였습니다."}
        else:
            raise HTTPException(status_code=400, detail="날짜가 지났습니다.")
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

@router.patch("/{leave_id}", summary="연차 수정", description="연차를 수정합니다.")
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

@router.delete("/{leave_id}", summary="연차 삭제", description="연차를 삭제합니다.")
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

import asyncio
from decimal import Decimal
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums.users import Status
from app.models.branches.user_leaves_days import UserLeaveInfo
from app.cruds.leave_histories.leave_histories_crud import (
    create_leave_history_record,
    create_user_leaves_days_record,
    delete_leave_history,
    fetch_approved_leave_data,
    fetch_leave_histories,
    fetch_user_details,
    get_leave_history_by_id,
    get_leave_history_by_id_and_branch,
    get_leave_info,
    get_user_by_id,
    get_user_info,
    get_user_leaves_days_record,
    update_leave_history,
    update_leave_history_status,
    update_user_leaves_days,
    update_user_total_leave_days,
)
from datetime import date, datetime, timedelta
from app.models.users.leave_histories_model import (
    LeaveHistoriesApprove,
    LeaveHistoriesCreate,
    LeaveHistoriesSearchDto,
    LeaveHistoriesUpdate,
)
from app.models.users.users_model import Users



async def get_user_leaves_service(
    branch_id: int,
    year: Optional[int],
    current_user_id: int,
    db: AsyncSession
) -> UserLeaveInfo:
    """현재 사용자의 연차 정보를 조회합니다."""
    year = year or date.today().year
    
    # 순차적으로 데이터 조회
    user = await get_user_info(current_user_id, db)
    leave_info = await get_leave_info(branch_id, year, current_user_id, db)
    
    if not leave_info:
        return UserLeaveInfo(
            user_id=current_user_id,
            branch_id=branch_id,
            year=year,
            increased_days=0.0,
            decreased_days=0.0,
            total_leave_days=user.total_leave_days,
            message=f"{year}년도의 연차 정보가 없습니다."
        )
    
    increased_days = float(leave_info.increased_days or 0.0)
    decreased_days = float(leave_info.decreased_days or 0.0)
    
    return UserLeaveInfo(
        user_id=current_user_id,
        branch_id=branch_id,
        year=year,
        increased_days=increased_days,
        decreased_days=decreased_days,
        total_leave_days=increased_days - decreased_days
    )


async def get_leave_histories_service(
    current_user: Users,
    db: AsyncSession,
    search: LeaveHistoriesSearchDto,
    date: Optional[date],
    branch_id: Optional[int],
    part_id: Optional[str],
    search_name: Optional[str],
    search_phone: Optional[str],
    page: int,
    size: int,
):
    """
    연차 신청 목록을 조회합니다.
    현재 로그인 한 회원의 권한이 사원 이상의 권한인 경우 조회할 수 있습니다.
    """
    if current_user.role not in [
        "MSO 최고권한",
        "최고관리자",
        "관리자",
        "통합관리자",
        "사원",
    ]:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    if date is None:
        date_obj = datetime.now().date()
        current_weekday = date_obj.weekday()
        date_start_day = date_obj - timedelta(days=current_weekday)
        date_end_day = date_start_day + timedelta(days=6)
    else:
        date_obj = date
        current_weekday = date_obj.weekday()
        date_start_day = date_obj - timedelta(days=current_weekday)
        date_end_day = date_start_day + timedelta(days=6)

    leave_histories, total_count = await fetch_leave_histories(
        current_user,
        db,
        search,
        date_start_day,
        date_end_day,
        branch_id,
        part_id,
        search_name,
        search_phone,
        page,
        size,
    )

    formatted_data = []
    for leave_history in leave_histories:
        user, branch, part, leave_category = await fetch_user_details(db, leave_history)
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
            "decreased_days": (
                float(leave_history.decreased_days)
                if leave_history.decreased_days is not None
                else 0.0
            ),
            "status": leave_history.status,
            "applicant_description": leave_history.applicant_description,
            "manager_id": leave_history.manager_id,
            "manager_name": leave_history.manager_name,
            "admin_description": leave_history.admin_description,
            "approve_date": leave_history.approve_date,
        }
        formatted_data.append(leave_history_data)

    return {
        "list": formatted_data,
        "pagination": {
            "total": total_count,
            "page": page,
            "size": size,
            "total_pages": (total_count + size - 1) // size,
        },
        "message": "연차 신청 목록을 정상적으로 조회하였습니다.",
    }


async def get_approve_leave_service(
    current_user: Users,
    db: AsyncSession,
    search: LeaveHistoriesSearchDto,
    date: Optional[date],
    branch_id: Optional[int],
    part_id: Optional[str],
    search_name: Optional[str],
    search_phone: Optional[str],
    page: int,
    size: int,
):
    """
    연차 전체 승인 목록을 조회합니다.
    현재 로그인 한 회원의 권한이 사원 이상의 권한인 경우 조회할 수 있습니다.
    선택한 한 주의 기간동안의 모든 회원의 연차 승인된 목록을 조회합니다.
    """
    if current_user.role not in [
        "MSO 최고권한",
        "최고관리자",
        "관리자",
        "통합관리자",
        "사원",
    ]:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    if current_user.role.strip() == "사원":
        raise HTTPException(status_code=403, detail="관리자(사원 이상)의 권한이 필요합니다.")        

    if date is None:
        date_obj = datetime.now().date()
        current_weekday = date_obj.weekday()
        date_start_day = date_obj - timedelta(days=current_weekday)
        date_end_day = date_start_day + timedelta(days=6)
    else:
        date_obj = date
        current_weekday = date_obj.weekday()
        date_start_day = date_obj - timedelta(days=current_weekday)
        date_end_day = date_start_day + timedelta(days=6)

    formatted_data, total_count = await fetch_approved_leave_data(
        db,
        search,
        date_start_day,
        date_end_day,
        branch_id,
        part_id,
        search_name,
        search_phone,
    )

    # 페이지네이션 적용
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_data = formatted_data[start_idx:end_idx]

    return {
        "list": paginated_data,
        "pagination": {
            "total": total_count,
            "page": page,
            "size": size,
            "total_pages": (total_count + size - 1) // size,
        },
        "message": "연차 전체 승인 목록을 정상적으로 조회하였습니다.",
    }


async def create_leave_history_service(
    leave_create: LeaveHistoriesCreate,
    branch_id: int,
    decreased_days: float,
    start_date: date,
    end_date: date,
    current_user_id: int,
    db: AsyncSession,
):
    """
    연차 신청을 합니다.
    만약 현재 사용자가 가지고 있는 연차 일수가 부족하게 되면 연차 신청을 할 수 없습니다.
    또한 하루에 여러번 신청할 수 있습니다.
    """
    current_user = await get_user_by_id(current_user_id, db)

    if current_user.role.strip() == "MSO 관리자":
        pass
    elif current_user.branch_id != branch_id:
        raise HTTPException(
            status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다."
        )

    if current_user.role not in ["MSO 최고권한", "최고관리자", "통합관리자", "사원"]:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

    leave_history_id = await create_leave_history_record(
        leave_create, branch_id, decreased_days, start_date, end_date, current_user, db
    )

    user_leaves_days_record = await get_user_leaves_days_record(current_user_id, db)

    if user_leaves_days_record is None:
        await create_user_leaves_days_record(
            current_user_id, branch_id, current_user, db
        )

    await db.commit()

    return {
        "message": "연차 생성에 성공하였습니다.",
        "leave_history_id": leave_history_id,
    }


async def approve_leave_service(
    leave_approve: LeaveHistoriesApprove,
    leave_id: int,
    branch_id: int,
    current_user_id: int,
    db: AsyncSession,
):
    """
    연차 승인/반려를 합니다.
    승인 시 현재 사용자의 연차 일수를 감소시키고 반려 시 현재 사용자의 연차 일수를 증가시킵니다.
    만약 승인 처리되었던 연차에 대해서 다시 승인 취소(반려) 처리를 하게 되면 현재 사용자의 연차 일수는 롤백됩니다.
    """
    current_user = await get_user_by_id(current_user_id, db)

    leave_history = await get_leave_history_by_id(leave_id, db)
    if not leave_history:
        raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

    now = datetime.now().date()
    if leave_approve.status == Status.APPROVED:
        leave_days_record = await get_user_leaves_days_record(leave_history.user_id, db)
        if not leave_days_record:
            raise HTTPException(
                status_code=404, detail="사용자의 연차 정보를 찾을 수 없습니다."
            )

        decreased_days = Decimal(str(leave_history.decreased_days))
        if leave_days_record.total_leave_days < decreased_days:
            raise HTTPException(
                status_code=400,
                detail=f"승인 불가: 신청 일수({decreased_days}일)가 남은 연차 일수({leave_days_record.total_leave_days}일)보다 많습니다.",
            )

        await update_user_leaves_days(leave_days_record, decreased_days, db)
        await update_user_total_leave_days(leave_history.user_id, decreased_days, db)

        await update_leave_history_status(
            leave_history, leave_approve, current_user, Status.APPROVED, db
        )
        message = "연차 승인에 성공하였습니다."

    elif leave_approve.status == Status.REJECTED:
        if leave_history.status == Status.APPROVED:
            await update_user_leaves_days(leave_days_record, -decreased_days, db)
            await update_user_total_leave_days(
                leave_history.user_id, -decreased_days, db
            )

        await update_leave_history_status(
            leave_history, leave_approve, current_user, Status.REJECTED, db
        )
        message = "연차 반려에 성공하였습니다."

    await db.flush()
    await db.commit()

    return {"message": message}


async def update_leave_service(
    leave_update: LeaveHistoriesUpdate,
    branch_id: int,
    leave_id: int,
    current_user_id: int,
    db: AsyncSession,
):
    """
    연차 수정을 합니다.
    현재 사용자의 연차 신청 목록을 불러와서 다시 수정할 수 있습니다.
    하지만 연차 신청 후 승인/반려인 경우에는 수정할 수 없습니다.
    """
    current_user = await get_user_by_id(current_user_id, db)

    if (
        current_user.branch_id != branch_id
        and current_user.role.strip() != "MSO 관리자"
    ):
        raise HTTPException(
            status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다."
        )
    if current_user.id != leave_history.user_id:
        raise HTTPException(status_code=403, detail="본인이 신청한 연차 이외의 연차는 수정할 수 없습니다.")

    leave_history = await get_leave_history_by_id_and_branch(leave_id, branch_id, db)
    if not leave_history:
        raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

    is_admin = current_user.role.strip() in [
        "MSO 최고권한",
        "최고관리자",
        "통합관리자",
    ]

    if leave_history.user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="연차를 수정할 권한이 없습니다.")

    await update_leave_history(leave_history, leave_update, db)
    await db.commit()

    return {"message": "연차 수정에 성공하였습니다."}


async def delete_leave_service(
    branch_id: int,
    leave_id: int,
    current_user_id: int,
    db: AsyncSession,
):
    """
    연차 삭제를 합니다.
    승인/반려된 연차는 삭제할 수 없습니다.
    완전한 삭제가 아닌 소프트 삭제를 진행합니다.
    이 또한 본인의 연차 신청 이외에는 삭제가 불가능합니다.
    """
    current_user = await get_user_by_id(current_user_id, db)

    if current_user.role.strip() == "MSO 관리자":
        pass
    elif current_user.branch_id != branch_id:
        raise HTTPException(
            status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다."
        )
    if current_user.id != leave_history.user_id:
        raise HTTPException(status_code=403, detail="본인이 신청한 연차 이외의 연차는 삭제할 수 없습니다.")

    leave_history = await get_leave_history_by_id_and_branch(leave_id, branch_id, db)
    if not leave_history:
        raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

    if (
        leave_history.request_user_id != current_user.id
        and current_user.role.strip()
        not in ["MSO 최고권한", "최고관리자", "통합관리자"]
    ):
        raise HTTPException(status_code=403, detail="연차를 삭제할 권한이 없습니다.")

    if leave_history.status.strip() != "확인중":
        raise HTTPException(
            status_code=400, detail="승인/반려된 연차는 삭제할 수 없습니다."
        )

    await delete_leave_history(leave_history, db)
    await db.commit()

    return {"message": "연차 삭제에 성공하였습니다."}

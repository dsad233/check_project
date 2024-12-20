from datetime import datetime, date, timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.middleware.tokenVerify import get_current_user, get_current_user_id
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.leave_histories_model import LeaveHistories, LeaveHistoriesCreate, LeaveHistoriesSearchDto, LeaveHistoriesUpdate
from app.models.users.users_model import Users
from app.models.branches.user_leaves_days import UserLeavesDays, UserLeavesDaysResponse
from app.models.branches.leave_categories_model import LeaveCategory
from app.enums.users import Status
from app.service.leave_histories_service import create_leave_history_service, delete_leave_service, get_leave_histories_service, get_user_leaves_service, update_leave_service

router = APIRouter()


@router.get(
    "/current-user-leaves",
    response_model=UserLeavesDaysResponse,
    summary="사원용 - 현재 사용자의 연차 일수 정보 조회",
    description="사원용 - 현재 사용자의 연차 일수 정보를 조회합니다.",
)
async def get_current_user_leaves(
    *,
    branch_id: Annotated[int, Query(description="지점 ID를 입력합니다.")],
    year: Annotated[
        Optional[int], Query(description="연도를 입력합니다. 예) 2024")
    ] = None,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    사원용 - 현재 사용자의 연차 일수 정보를 조회합니다.
    """
    try:
        return await get_user_leaves_service(branch_id, year, current_user_id, db)
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))



@router.post("", summary="사원용 - 연차 신청", description="사원용 - 연차를 신청합니다.")
async def create_leave_history(
    context: Request,
    leave_create: LeaveHistoriesCreate,
    branch_id: Annotated[
        int, Query(description="현재 사용자가 포함된 지점 ID를 입력합니다.")
    ],
    decreased_days: Annotated[
        float,
        Query(description="사용할 연차 일수를 입력합니다. 타입은 float입니다. 예) 1.0"),
    ],
    start_date: Annotated[
        date, Query(description="시작일을 입력합니다. 예) YYYY-MM-DD")
    ],
    end_date: Annotated[date, Query(description="종료일을 입력합니다. 예) YYYY-MM-DD")],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    사원용 - 연차를 신청합니다.
    """
    try:
        return await create_leave_history_service(
            leave_create,
            branch_id,
            decreased_days,
            start_date,
            end_date,
            current_user_id,
            db,
        )
    except Exception as err:
        print(f"연차 생성 중 오류 발생: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    

@router.get(
    "",
    summary="사원용 - 연차 신청 목록 조회",
    description="사원용 - 연차 신청 목록을 조회합니다.",
)
async def get_leave_histories(
    context: Request,
    current_user: Annotated[Users, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    search: Annotated[LeaveHistoriesSearchDto, Depends()],
    date: Annotated[
        Optional[date],
        Query(
            description="시작일 계산을 위한 날짜를 입력합니다. 공백인 경우 오늘을 포함한 주의 일요일-토요일 기간을 조회합니다. 예) YYYY-MM-DD"
        ),
    ] = None,
    branch_id: Annotated[
        Optional[int],
        Query(description="검색할 지점 ID를 입력합니다. 공백인 경우 전체 조회합니다."),
    ] = None,
    part_id: Annotated[
        Optional[str],
        Query(description="검색할 파트 ID를 입력합니다. 공백인 경우 전체 조회합니다."),
    ] = None,
    search_name: Annotated[
        Optional[str],
        Query(description="검색할 이름을 입력합니다. 공백인 경우 전체 조회합니다."),
    ] = None,
    search_phone: Annotated[
        Optional[str],
        Query(description="검색할 전화번호를 입력합니다. 공백인 경우 전체 조회합니다."),
    ] = None,
    page: Annotated[
        int, Query(description="페이지 번호를 입력합니다. 기본값은 1입니다.")
    ] = 1,
    size: Annotated[
        int, Query(description="페이지당 레코드 수를 입력합니다. 기본값은 10입니다.")
    ] = 10,
):
    """
    사원용 - 연차 신청 목록을 조회합니다.
    """
    try:
        return await get_leave_histories_service(
            current_user,
            db,
            search,
            date,
            branch_id,
            part_id,
            search_name,
            search_phone,
            page,
            size,
        )
    except Exception as err:
        print(f"에러가 발생하였습니다: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    

@router.patch(
    "/{leave_id}", summary="사원용 - 연차 수정", description="사원용 - 연차를 수정합니다."
)
async def update_leave(
    leave_update: LeaveHistoriesUpdate,
    branch_id: Annotated[
        int, Query(description="현재 사용자가 포함된 지점 ID를 입력합니다.")
    ],
    leave_id: Annotated[int, Path(description="수정할 연차 ID를 입력합니다.")],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    사원용 - 연차를 수정합니다.
    """
    try:
        return await update_leave_service(
            leave_update, branch_id, leave_id, current_user_id, db
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.delete(
    "/{leave_id}", summary="사원용 - 연차 삭제", description="사원용 - 연차를 삭제합니다."
)
async def delete_leave(
    branch_id: Annotated[
        int, Query(..., description="현재 사용자가 포함된 지점 ID를 입력합니다.")
    ],
    leave_id: Annotated[int, Path(..., description="삭제할 연차 ID를 입력합니다.")],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    사원용 - 연차를 삭제합니다.
    """
    try:
        return await delete_leave_service(
            branch_id, leave_id, current_user_id, db
        )
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))
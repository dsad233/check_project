from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.users.leave_histories_model import LeaveHistories, LeaveHistoriesResponse, LeaveHistoriesCreate, LeaveHistoriesListResponse, LeaveHistoriesSearchDto, LeaveHistoriesApprove, LeaveHistoriesUpdate
from app.models.users.users_model import Users
from app.common.dto.pagination_dto import PaginationDto

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

@router.get("", response_model=LeaveHistoriesListResponse)
async def get_leave_histories(
    branch_id: int, 
    search: LeaveHistoriesSearchDto = Depends(), 
    current_user_id: int = Depends(get_current_user_id)
)-> LeaveHistoriesListResponse:
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.role.strip() in ["최고관리자", "파트관리자", "통합관리자"]:
            if current_user.branch_id != branch_id:
                raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")
        else:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        count_query = select(func.count()).select_from(LeaveHistories).where(LeaveHistories.branch_id == branch_id, LeaveHistories.deleted_yn == 'N')
        count_result = await db.execute(count_query)
        count = count_result.scalar_one_or_none()
        
        pagination = PaginationDto(total_record=count)
        
        query = select(LeaveHistories).options(
            joinedload(LeaveHistories.user).joinedload(Users.part),
            joinedload(LeaveHistories.user),
            joinedload(LeaveHistories.leave_category),
            joinedload(LeaveHistories.branch),
        ).offset(search.offset).limit(search.record_size).where(
            LeaveHistories.branch_id == branch_id, 
            LeaveHistories.deleted_yn == 'N'
        )
        
        if search.kind:
            query = query.join(LeaveHistories.leave_category).filter(LeaveHistories.leave_category.has(name=search.kind))
        if search.status:
            query = query.filter(LeaveHistories.status == search.status)
        
        result = await db.execute(query)
        leave_histories = result.scalars().all()
        
        leave_history_dtos = []

        for history in leave_histories:
            dto = LeaveHistoriesResponse(
                id=history.id,
                branch_name=history.branch.name,
                user_name=history.user.name,
                part_name=history.user.part.name,
                
                application_date=history.application_date,
                leave_category_name=history.leave_category.name,
                
                status=history.status,
                applicant_description=history.applicant_description,
                admin_description=history.admin_description,
                approve_date=history.approve_date
            )
            leave_history_dtos.append(dto)
            
        leave_list_response = LeaveHistoriesListResponse(list=leave_history_dtos, pagination=pagination) 
        return leave_list_response
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

@router.post("")
async def create_leave_history(
    branch_id: int,
    leave_create: LeaveHistoriesCreate,
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")

        create = LeaveHistories(
            branch_id=branch_id,
            user_id=current_user.id,
            leave_category_id=leave_create.leave_category_id,
            application_date=leave_create.date,
            applicant_description=leave_create.applicant_description or None,
            status = "승인"
        )

        db.add(create)
        await db.commit()
        return {"message": "연차 생성에 성공하였습니다."}
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/{leave_id}")
async def approve_leave(
    leave_id: int,
    branch_id: int,
    leave_approve: LeaveHistoriesApprove,
    current_user_id: int = Depends(get_current_user_id),
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
            await db.commit()
            return {"message": "연차 승인/반려에 성공하였습니다."}
        else:
            raise HTTPException(status_code=400, detail="날짜가 지났습니다.")
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.patch("/{leave_id}")
async def update_leave(
    branch_id: int,
    leave_id: int,
    leave_update: LeaveHistoriesUpdate,
    current_user_id: int = Depends(get_current_user_id),
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

        if leave_history.user_id != current_user.id and current_user.role.strip() not in ["MSO 최고권한", "최고관리자", "통합관리자"]:
            raise HTTPException(status_code=403, detail="연차를 삭제할 권한이 없습니다.")

        if leave_history.status.strip() != "확인중":
            raise HTTPException(status_code=400, detail="승인/반려된 연차는 삭제할 수 없습니다.")

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


@router.delete("/{leave_id}")
async def delete_leave(
    branch_id: int, leave_id: int, current_user_id: int = Depends(get_current_user_id)
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

        if leave_history.user_id != current_user.id and current_user.role.strip() not in ["MSO 최고권한", "최고관리자", "통합관리자"]:
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

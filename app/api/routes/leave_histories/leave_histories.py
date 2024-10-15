from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.users.leave_histories_model import LeaveHistories, LeaveHistoriesResponse, LeaveHistoriesCreate
from app.models.users.users_model import Users

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


@router.get("")
async def get_leave_histories(
    branch_id: int, current_user_id: int = Depends(get_current_user_id)
)-> list[LeaveHistoriesResponse]:
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.role.strip() in ["최고관리자", "파트관리자"]:
            if current_user.branch_id != branch_id:
                raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")
        else:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        query = select(LeaveHistories).options(
            joinedload(LeaveHistories.user).joinedload(Users.part),
            joinedload(LeaveHistories.user).joinedload(Users.branch),
            joinedload(LeaveHistories.leave_category)
        ).where(LeaveHistories.branch_id == branch_id, LeaveHistories.deleted_yn == 'N')
        result = await db.execute(query)
        leave_histories = result.scalars().all()
        
        leave_history_dtos = []

        for history in leave_histories:
            dto = LeaveHistoriesResponse(
                id=history.id,
                branch_name=history.user.branch.name,
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
        return leave_history_dtos
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# @router.get("/pending")
# async def getPendingAnnualLeave(current_user: Users = Depends(validate_token)):
#     if current_user.role.strip() == "사원":
#         raise HTTPException(status_code=403, detail="권한이 없습니다.")
#     try:
#         query = (
#             select(AnnualLeave)
#             .options(
#                 selectinload(AnnualLeave.proposer), selectinload(AnnualLeave.manager)
#             )
#             .where(
#                 AnnualLeave.application_status == "pending",
#                 AnnualLeave.deleted_yn == "N",
#             )
#         )
#         result = await annualleaves.execute(query)
#         annual_leaves = result.scalars().all()

#         annual_leave_dtos = []
#         for leave in annual_leaves:
#             dto = AnnualLeaveListsResponse(
#                 id=leave.annual_leave_id,
#                 proposer_name=leave.proposer.name,
#                 work_part=leave.proposer.part,
#                 application_date=leave.application_date,
#                 type=leave.type,
#                 date_count=leave.date_count,
#                 status=leave.application_status,
#                 proposer_note=leave.proposer_note,
#                 manager_note=leave.manager_note if leave.manager_note else "",
#                 updated_at=leave.updated_at,
#                 manager_name=leave.manager.name,
#             )
#             annual_leave_dtos.append(dto)
#         return {"message": "연차 조회에 성공하였습니다.", "data": annual_leave_dtos}
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# @router.post("")
# async def createAnnualLeave(
#     annualLeaveCreate: AnnualLeaveCreate,
#     current_user: Users = Depends(validate_token),
# ):
#     try:
#         create = AnnualLeave(
#             manager_id=annualLeaveCreate.manager_id,
#             type=annualLeaveCreate.type,
#             proposer_id=current_user.id,
#             date_count=annualLeaveCreate.date_count,
#             application_date=annualLeaveCreate.application_date,
#             proposer_note=annualLeaveCreate.proposer_note,
#         )

#         annualleaves.add(create)
#         await annualleaves.commit()
#         return {"message": "연차 생성에 성공하였습니다."}
#     except Exception as err:
#         await annualleaves.rollback()
#         print(err)
#         raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# @router.post("/{id}")
# async def approveAnnualLeave(
#     id: int,
#     annualLeaveApprove: AnnualLeaveApprove,
#     current_user: Users = Depends(validate_token),
# ):
#     try:
#         if current_user.role.strip() == "사원":
#             raise HTTPException(status_code=403, detail="권한이 없습니다.")

#         query = select(AnnualLeave).where(AnnualLeave.annual_leave_id == id)
#         result = await annualleaves.execute(query)
#         annual_leave = result.scalar_one_or_none()

#         if not annual_leave:
#             raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

#         if annual_leave.application_status == "pending":
#             annual_leave.status = annualLeaveApprove.status
#             annual_leave.manager_id = current_user.id
#             annual_leave.manager_note = annualLeaveApprove.manager_note
#             await annualleaves.commit()
#             return {"message": "연차 승인/반려에 성공하였습니다."}
#         else:
#             raise HTTPException(status_code=400, detail="이미 승인/반려된 연차입니다.")
#     except HTTPException:
#         raise
#     except Exception as err:
#         await annualleaves.rollback()
#         print(err)
#         raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# @router.patch("/{id}")
# async def updateAnnualLeave(
#     id: int,
#     annualLeaveUpdate: AnnualLeaveUpdate,
#     current_user: Users = Depends(validate_token),
# ):
#     try:
#         query = select(AnnualLeave).where(AnnualLeave.annual_leave_id == id)
#         result = await annualleaves.execute(query)
#         annual_leave = result.scalar_one_or_none()

#         if not annual_leave:
#             raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

#         if annual_leave.proposer_id != current_user.id:
#             raise HTTPException(
#                 status_code=403, detail="연차를 수정할 권한이 없습니다."
#             )

#         if annual_leave.application_status != "pending":
#             raise HTTPException(
#                 status_code=400, detail="승인/반려된 연차는 수정할 수 없습니다."
#             )

#         annual_leave.type = annualLeaveUpdate.type
#         annual_leave.date_count = annualLeaveUpdate.date_count
#         annual_leave.application_date = annualLeaveUpdate.application_date
#         annual_leave.proposer_note = annualLeaveUpdate.proposer_note
#         await annualleaves.commit()
#         return {"message": "연차 수정에 성공하였습니다."}
#     except HTTPException:
#         raise
#     except Exception as err:
#         await annualleaves.rollback()
#         print(err)
#         raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# @router.delete("/{id}")
# async def deleteAnnualLeave(id: int, current_user: Users = Depends(validate_token)):
#     try:
#         query = select(AnnualLeave).where(AnnualLeave.annual_leave_id == id)
#         result = await annualleaves.execute(query)
#         annual_leave = result.scalar_one_or_none()

#         if not annual_leave:
#             raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

#         if annual_leave.proposer_id != current_user.id:
#             raise HTTPException(
#                 status_code=403, detail="연차를 삭제할 권한이 없습니다."
#             )

#         if annual_leave.application_status != "pending":
#             raise HTTPException(
#                 status_code=400, detail="승인/반려된 연차는 삭제할 수 없습니다."
#             )

#         annual_leave.deleted_yn = "Y"
#         await annualleaves.commit()
#         return {"message": "연차 삭제에 성공하였습니다."}
#     except HTTPException:
#         raise
#     except Exception as err:
#         await annualleaves.rollback()
#         print(err)
#         raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

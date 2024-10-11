from app.core.database import async_session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.middleware.tokenVerify import vaildate_Token
from app.api.routes.annual_leaves.schema.annual_leave_schema import AnnualLeaveCreate, AnnualLeaveApprove, AnnualLeaveUpdate, AnnualLeaveListsResponse
from app.models.models import AnnualLeave, Users
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter(dependencies=[Depends(vaildate_Token)])
annualleaves = async_session()

@router.get('')
async def getAnnualLeave(
    current_user: Users = Depends(vaildate_Token)
):
    try:
        query = (
            select(AnnualLeave)
            .options(selectinload(AnnualLeave.proposer), selectinload(AnnualLeave.manager))
            .where(AnnualLeave.proposer_id == current_user.id, AnnualLeave.deleted_yn == 'N')
        )
        result = await annualleaves.execute(query)
        annual_leaves = result.scalars().all()
        annual_leave_dtos=[]    
        
        for leave in annual_leaves:   
            dto = AnnualLeaveListsResponse(
                id = leave.annual_leave_id,
                proposer_name = leave.proposer.name,
                work_part = leave.proposer.part,
                application_date = leave.application_date,
                type = leave.type,
                date_count = leave.date_count,
                status = leave.application_status,
                proposer_note = leave.proposer_note,
                manager_note = leave.manager_note if leave.manager_note else "",
                updated_at = leave.updated_at,
                manager_name = leave.manager.name
            )
            annual_leave_dtos.append(dto)
        return { "message" : "연차 조회에 성공하였습니다.", "data" : annual_leave_dtos }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")

@router.get('/pending')
async def getPendingAnnualLeave(
    current_user: Users = Depends(vaildate_Token)
):
    if current_user.role.strip() == "사원":
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    try:
        query = (
            select(AnnualLeave)
            .options(selectinload(AnnualLeave.proposer), selectinload(AnnualLeave.manager))
            .where(AnnualLeave.application_status == "pending", AnnualLeave.deleted_yn == 'N')
        )
        result = await annualleaves.execute(query)
        annual_leaves = result.scalars().all()

        annual_leave_dtos=[]    
        for leave in annual_leaves:
            dto = AnnualLeaveListsResponse(
                id = leave.annual_leave_id,
                proposer_name = leave.proposer.name,
                work_part = leave.proposer.part,
                application_date = leave.application_date,
                type = leave.type,
                date_count = leave.date_count,
                status = leave.application_status,
                proposer_note = leave.proposer_note,
                manager_note = leave.manager_note if leave.manager_note else "",
                updated_at = leave.updated_at,
                manager_name = leave.manager.name
            )
            annual_leave_dtos.append(dto)
        return { "message" : "연차 조회에 성공하였습니다.", "data" : annual_leave_dtos }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다." )

@router.post('')
async def createAnnualLeave(
    annualLeaveCreate: AnnualLeaveCreate,
    current_user: Users = Depends(vaildate_Token),
):
    try:
        create = AnnualLeave(
            manager_id = annualLeaveCreate.manager_id,
            type = annualLeaveCreate.type,
            proposer_id = current_user.id,
            date_count = annualLeaveCreate.date_count,
            application_date = annualLeaveCreate.application_date,
            proposer_note = annualLeaveCreate.proposer_note,
        )
        
        annualleaves.add(create)
        await annualleaves.commit()
        return { "message" : "연차 생성에 성공하였습니다." }    
    except Exception as err:
        await annualleaves.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

@router.post('/{id}')
async def approveAnnualLeave(
    id : int,
    annualLeaveApprove: AnnualLeaveApprove,
    current_user: Users = Depends(vaildate_Token),
):
    try:
        if current_user.role.strip() == "사원":
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        query = select(AnnualLeave).where(AnnualLeave.annual_leave_id == id)
        result = await annualleaves.execute(query)
        annual_leave = result.scalar_one_or_none()
        
        if not annual_leave:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")
        
        if annual_leave.application_status == "pending":
            annual_leave.status = annualLeaveApprove.status
            annual_leave.manager_id = current_user.id
            annual_leave.manager_note = annualLeaveApprove.manager_note
            await annualleaves.commit() 
            return { "message" : "연차 승인/반려에 성공하였습니다." }
        else:
            raise HTTPException(status_code=400, detail="이미 승인/반려된 연차입니다.")
    except HTTPException:
        raise
    except Exception as err:
        await annualleaves.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

@router.patch('/{id}')
async def updateAnnualLeave(
    id : int,
    annualLeaveUpdate: AnnualLeaveUpdate,
    current_user: Users = Depends(vaildate_Token)
):
    try:
        query = select(AnnualLeave).where(AnnualLeave.annual_leave_id == id)
        result = await annualleaves.execute(query)
        annual_leave = result.scalar_one_or_none()
        
        if not annual_leave:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")
        
        if annual_leave.proposer_id != current_user.id:
            raise HTTPException(status_code=403, detail="연차를 수정할 권한이 없습니다.")
        
        if annual_leave.application_status != "pending":
            raise HTTPException(status_code=400, detail="승인/반려된 연차는 수정할 수 없습니다.")
        
        annual_leave.type = annualLeaveUpdate.type
        annual_leave.date_count = annualLeaveUpdate.date_count
        annual_leave.application_date = annualLeaveUpdate.application_date
        annual_leave.proposer_note = annualLeaveUpdate.proposer_note
        await annualleaves.commit()
        return { "message" : "연차 수정에 성공하였습니다." }
    except HTTPException:
        raise
    except Exception as err:
        await annualleaves.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

@router.delete('/{id}')
async def deleteAnnualLeave(
    id : int,
    current_user: Users = Depends(vaildate_Token)
):
    try:
        query = select(AnnualLeave).where(AnnualLeave.annual_leave_id == id)
        result = await annualleaves.execute(query)
        annual_leave = result.scalar_one_or_none()
        
        if not annual_leave:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")
        
        if annual_leave.proposer_id != current_user.id:
            raise HTTPException(status_code=403, detail="연차를 삭제할 권한이 없습니다.")
        
        if annual_leave.application_status != "pending":
            raise HTTPException(status_code=400, detail="승인/반려된 연차는 삭제할 수 없습니다.")
        
        annual_leave.deleted_yn = 'Y'
        await annualleaves.commit()
        return { "message" : "연차 삭제에 성공하였습니다." }
    except HTTPException:
        raise
    except Exception as err:
        await annualleaves.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
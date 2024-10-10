from app.core.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.middleware.tokenVerify import vaildate_Token
from app.api.routes.annual_leaves.schema.annual_leave_schema import AnnualLeaveCreate, AnnualLeaveStatus, AnnualLeaveApprove, AnnualLeaveUpdate
from app.models.models import AnnualLeave, Users

router = APIRouter(dependencies=[Depends(vaildate_Token)])

@router.get('')
async def getAnnualLeave(
    current_user: Users = Depends(vaildate_Token),
    db: Session = Depends(get_db)
):
    try:
        getAnnualLeave = db.query(AnnualLeave).filter(AnnualLeave.proposer_id == current_user.id, AnnualLeave.deleted_yn == 'N').all()
        return { "message" : "연차 조회에 성공하였습니다.", "data" : getAnnualLeave }
    except Exception as err:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다." + err)

@router.get('/pending')
async def getPendingAnnualLeave(
    current_user: Users = Depends(vaildate_Token),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    try:
        getPendingAnnualLeave = db.query(AnnualLeave).filter(AnnualLeave.status == AnnualLeaveStatus.PENDING, AnnualLeave.deleted_yn == 'N').all()
        return { "message" : "연차 조회에 성공하였습니다.", "data" : getPendingAnnualLeave }
    except Exception as err:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다." + err)

@router.post('')
async def createAnnualLeave(
    annualLeaveCreate: AnnualLeaveCreate,
    current_user: Users = Depends(vaildate_Token),
    db: Session = Depends(get_db)
):
    try:
        create = AnnualLeave(
            type = annualLeaveCreate.type,
            proposer_id = current_user.id,
            date_count = annualLeaveCreate.date_count,
            application_date = annualLeaveCreate.application_date,
            proposer_note = annualLeaveCreate.proposer_note,
        )
        db.add(create)
        db.commit()
        return { "message" : "연차 생성에 성공하였습니다." }    
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

@router.post('/{id}')
async def approveAnnualLeave(
    id : int,
    annualLeaveApprove: AnnualLeaveApprove,
    current_user: Users = Depends(vaildate_Token),
    db: Session = Depends(get_db)
):
    try:
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        annual_leave = db.query(AnnualLeave).filter(AnnualLeave.id == id).first()
        if not annual_leave:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")
        
        if annual_leave.status == AnnualLeaveStatus.PENDING:
            annual_leave.status = annualLeaveApprove.status
            annual_leave.manager_id = current_user.id
            annual_leave.manager_note = annualLeaveApprove.manager_note
            db.commit()
            return { "message" : "연차 승인/반려에 성공하였습니다." }
        else:
            raise HTTPException(status_code=400, detail="이미 승인/반려된 연차입니다.")
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

@router.patch('/{id}')
async def updateAnnualLeave(
    id : int,
    annualLeaveUpdate: AnnualLeaveUpdate,
    current_user: Users = Depends(vaildate_Token),
    db: Session = Depends(get_db)
):
    try:
        annual_leave = db.query(AnnualLeave).filter(AnnualLeave.id == id, AnnualLeave.deleted_yn == 'N').first()
        if not annual_leave:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")
        
        if annual_leave.proposer_id != current_user.id:
            raise HTTPException(status_code=403, detail="연차를 수정할 권한이 없습니다.")
        
        if annual_leave.status != AnnualLeaveStatus.PENDING:
            raise HTTPException(status_code=400, detail="승인/반려된 연차는 수정할 수 없습니다.")
        
        annual_leave.type = annualLeaveUpdate.type
        annual_leave.date_count = annualLeaveUpdate.date_count
        annual_leave.application_date = annualLeaveUpdate.application_date
        annual_leave.proposer_note = annualLeaveUpdate.proposer_note
        db.commit()
        return { "message" : "연차 수정에 성공하였습니다." }
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다." + err)

@router.delete('/{id}')
async def deleteAnnualLeave(
    id : int,
    current_user: Users = Depends(vaildate_Token),
    db: Session = Depends(get_db)
):
    try:
        annual_leave = db.query(AnnualLeave).filter(AnnualLeave.id == id, AnnualLeave.deleted_yn == 'N').first()
        if not annual_leave:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")
        
        if annual_leave.proposer_id != current_user.id:
            raise HTTPException(status_code=403, detail="연차를 삭제할 권한이 없습니다.")
        
        if annual_leave.status != AnnualLeaveStatus.PENDING:
            raise HTTPException(status_code=400, detail="승인/반려된 연차는 삭제할 수 없습니다.")
        
        annual_leave.deleted_yn = 'Y'
        db.commit()
        return { "message" : "연차 삭제에 성공하였습니다." }
    except HTTPException:
        raise
    except Exception as err:
        db.rollback()
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다." + err)
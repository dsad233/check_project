from app.core.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.middleware.tokenVerify import vaildate_Token
from app.api.routes.annual_leaves.schema.annual_leave_schema import AnnualLeaveCreate
from app.models.models import AnnualLeave, Users
from app.api.routes.annual_leaves.schema.annual_leave_schema import AnnualLeaveStatus, AnnualLeaveApprove, AnnualLeaveUpdate

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
        print("에러가 발생하였습니다.")
        print(err)
        
@router.get('/pending')
async def getPendingAnnualLeave(
    db: Session = Depends(get_db)
):
    try:
        getPendingAnnualLeave = db.query(AnnualLeave).filter(AnnualLeave.status == AnnualLeaveStatus.PENDING, AnnualLeave.deleted_yn == 'N').all()
        return { "message" : "연차 조회에 성공하였습니다.", "data" : getPendingAnnualLeave }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)

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
        print("에러가 발생하였습니다.")
        print(err)
        
@router.post('/{id}')
async def approveAnnualLeave(
    id : int,
    annualLeaveApprove: AnnualLeaveApprove,
    current_user: Users = Depends(vaildate_Token),
    db: Session = Depends(get_db)
):
    try:
        annual_leave = db.query(AnnualLeave).filter(AnnualLeave.id == id).first()
        
        if annual_leave.status == AnnualLeaveStatus.PENDING:
            annual_leave.status = annualLeaveApprove.status
            annual_leave.manager_id = current_user.id
            annual_leave.manager_note = annualLeaveApprove.manager_note
            db.commit()
            return { "message" : "연차 승인/반려에 성공하였습니다." }
        else:
            return { "message" : "이미 승인/반려된 연차입니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        
@router.patch('/{id}')
async def updateAnnualLeave(
    id : int,
    annualLeaveUpdate: AnnualLeaveUpdate,
    current_user: Users = Depends(vaildate_Token),
    db: Session = Depends(get_db)
):
    try:
        annual_leave = db.query(AnnualLeave).filter(AnnualLeave.id == id, AnnualLeave.deleted_yn == 'N').first()
        
        if annual_leave.proposer_id == current_user.id:
            annual_leave.type = annualLeaveUpdate.type
            annual_leave.date_count = annualLeaveUpdate.date_count
            annual_leave.application_date = annualLeaveUpdate.application_date
            annual_leave.proposer_note = annualLeaveUpdate.proposer_note
            db.commit()
            return { "message" : "연차 수정에 성공하였습니다." }
        else:
            return { "message" : "승인/반려된 연차는 수정할 수 없습니다." }
        
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        
@router.delete('/{id}')
async def deleteAnnualLeave(
    id : int,
    current_user: Users = Depends(vaildate_Token),
    db: Session = Depends(get_db)
):
    try:
        annual_leave = db.query(AnnualLeave).filter(AnnualLeave.id == id).first()
        if annual_leave.proposer_id == current_user.id:
            annual_leave.deleted_yn = 'Y'
            db.commit()
            return { "message" : "연차 삭제에 성공하였습니다." }
        else:
            return { "message" : "승인/반려된 연차는 삭제할 수 없습니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
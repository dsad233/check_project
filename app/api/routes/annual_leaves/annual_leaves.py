from app.core.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.middleware.tokenVerify import vaildate_Token
from app.api.routes.annual_leaves.schema.annual_leave_schema import AnnualLeaveCreate
from app.models.models import AnnualLeave, Users
from app.api.routes.annual_leaves.schema.annual_leave_schema import AnnualLeaveStatus, AnnualLeaveApprove

router = APIRouter(dependencies=[Depends(vaildate_Token)])

@router.get('')
async def getAnnualLeave(
    current_user: Users = Depends(vaildate_Token),
    db: Session = Depends(get_db)
):
    try:
        getAnnualLeave = db.query(AnnualLeave).filter(AnnualLeave.proposer_id == current_user.id).all()
        return { "message" : "연차 조회에 성공하였습니다.", "data" : getAnnualLeave }
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
            return { "message" : "연차 승인에 성공하였습니다." }
        else:
            return { "message" : "이미 승인/반려된 연차입니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
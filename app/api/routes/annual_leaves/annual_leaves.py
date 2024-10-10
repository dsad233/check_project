from app.api.core.database import Session
from fastapi import APIRouter, Depends
from app.api.middleware.tokenVerify import vaildate_Token
from app.api.routes.annual_leaves.schema.annual_leave_schema import AnnualLeaveCreate
from app.api.models.models import AnnualLeave, Users
from app.api.routes.annual_leaves.schema.annual_leave_schema import AnnualLeaveStatus

router = APIRouter(dependencies=[Depends(vaildate_Token)])
annual_leaves = Session()

@router.get('')
async def getAnnualLeave(
    current_user: Users = Depends(vaildate_Token)
):
    try:
        getAnnualLeave = annual_leaves.query(AnnualLeave).filter(AnnualLeave.proposer_id == current_user.id).all()
        return { "message" : "연차 조회에 성공하였습니다.", "data" : getAnnualLeave }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)

@router.post('')
async def createAnnualLeave(
    annualLeaveCreate: AnnualLeaveCreate,
    current_user: Users = Depends(vaildate_Token)
):
    try:
        create = AnnualLeave(
            type = annualLeaveCreate.type,
            proposer_id = current_user.id,
            date_count = annualLeaveCreate.date_count,
            application_date = annualLeaveCreate.application_date,
            proposer_note = annualLeaveCreate.proposer_note,
        )
        annual_leaves.add(create)
        annual_leaves.commit()
        return { "message" : "연차 생성에 성공하였습니다." }    
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
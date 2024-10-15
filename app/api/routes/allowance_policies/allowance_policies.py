from fastapi import APIRouter, Depends, HTTPException
from app.middleware.tokenVerify import validate_token
from app.core.database import async_session
from sqlalchemy.future import select
from app.models.users.users_model import Users
from app.models.parts.allowance_policies_model import AllowancePolicies, AllowancePoliciesCreate, AllowancePoliciesUpdate
from typing import Annotated


router = APIRouter(dependencies= [Depends(validate_token)])
allowance_policies = async_session()

# 수당 데이터 생성
@router.post("/parts/{part_id}/allowance_policies")
async def create_allowance_policies(part_id : int, allowancePoliciesCreate : AllowancePoliciesCreate, token=Annotated[Users, Depends(validate_token)]):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자" | token.role != "관리자":
            raise HTTPException(status_code=403, detail="생성 권한이 없습니다.")

        new_allowance_Policies = AllowancePolicies(
            part_id = part_id,
            comprehensive_overtime = allowancePoliciesCreate.comprehensive_overtime,
            annual_leave = allowancePoliciesCreate.annual_leave,
            holiday_work = allowancePoliciesCreate.holiday_work,
            job_duty = allowancePoliciesCreate.job_duty,
            meal = allowancePoliciesCreate.meal
        )

        await allowance_policies.add(new_allowance_Policies)
        await allowance_policies.commit()
        await allowance_policies.refresh(new_allowance_Policies)


        return {
            "message": "성공적으로 수당 데이터 생성을 하였습니다."
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail="수당 데이터 생성에 실패하였습니다.")
    


# 수당 데이터 수정
@router.patch("/parts/{part_id}/allowance_policies/{id}")
async def find_one_allowance_policies(part_id : int, id : int, allowancePoliciesUpdate : AllowancePoliciesUpdate, token=Annotated[Users, Depends(validate_token)]):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자" | token.role != "관리자":
            raise HTTPException(status_code=403, detail="생성 권한이 없습니다.")

        find_one_allowance_policies = await allowance_policies.execute(select(AllowancePolicies).where(AllowancePolicies.part_id == part_id, AllowancePolicies.id == id, AllowancePolicies.deleted_yn == "N"))
        result = find_one_allowance_policies.scalar_one_or_none()
        
        if(result == None):
            raise HTTPException(status_code=404, detail="수당 데이터가 존재하지 않습니다.")
        
        result.comprehensive_overtime = allowancePoliciesUpdate.comprehensive_overtime
        result.annual_leave = allowancePoliciesUpdate.annual_leave
        result.holiday_work = allowancePoliciesUpdate.holiday_work
        result.job_duty = allowancePoliciesUpdate.job_duty
        result.meal = allowancePoliciesUpdate.meal

        await allowance_policies.commit()

        return {
            "message": "성공적으로 수당 데이터를 수정 하였습니다."
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail="수당 데이터 수정에 실패하였습니다.")
    
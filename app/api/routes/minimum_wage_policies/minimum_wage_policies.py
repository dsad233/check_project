from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import ForbiddenError
from app.core.database import get_db
from app.cruds.minimum_wage_policies import minimum_wage_policies_crud
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.common.minimum_wage_policies_model import MinimumWagePolicyDto, MinimumWagePolicy
from app.exceptions.exceptions import NotFoundError
router = APIRouter(dependencies=[Depends(validate_token)])

@router.get("/get", response_model=MinimumWagePolicyDto)
async def get_minimum_wage_policy(session: AsyncSession = Depends(get_db)) -> MinimumWagePolicyDto:
    try:
        print("여기여기여기")
        minimum_wage_policy = await minimum_wage_policies_crud.find(session=session)
        print("여기여기여기2")
        if minimum_wage_policy is None:
            raise NotFoundError(f"최저시급 정책을 찾을 수 없습니다.")
        print("여기여기여기3")
        return minimum_wage_policy
    except Exception as error:
        print(f"오류 발생 : {error}")

@router.patch("/update", response_model=str)
async def update_minimum_wage_policy(minimum_wage_policy_update: MinimumWagePolicyDto, session: AsyncSession = Depends(get_db)) -> str:
    await minimum_wage_policies_crud.update(session=session, minimum_wage_policy_update=MinimumWagePolicy(**minimum_wage_policy_update.model_dump()))
    return "최저시급 정책이 업데이트되었습니다."
from fastapi import APIRouter, Depends
from app.models.policies.branchpolicies import OverTimePolicies
from typing import Annotated
from app.middleware.tokenVerify import validate_token
from app.core.database import async_session


router = APIRouter(dependencies= Depends(validate_token))
overtime_policies
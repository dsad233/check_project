from datetime import date

from pydantic_settings import BaseSettings
from typing import Optional


class BranchCreateEnum:
    attendance = "근태"
    position = "직책"
    counseling_performance = "상담실적"
    doctor = "의사"
    budget = "예산"


class BranchCreate(BaseSettings):
    branch_id: int
    name: str
    policy_type: BranchCreateEnum
    effective_from: date


class BranchUpdate(BaseSettings):
    name: str
    policy_type: BranchCreateEnum
    effective_to: Optional[date] = None

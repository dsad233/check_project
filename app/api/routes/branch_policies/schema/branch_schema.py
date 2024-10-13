from datetime import date

from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Optional
from fastapi import HTTPException


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

    @field_validator("name")
    @classmethod
    def name_none_check(cls, name):
        if(name == None):
            raise HTTPException(status_code=400, detail="지점 정책명 작성란이 누락되었습니다. 다시 작성해주세요.")
        return name

    @field_validator("name")
    @classmethod
    def name_len_check(cls, name_len):
        if(len(name_len.strip()) < 1):
            raise HTTPException(status_code=400, detail="2자 이상으로 지점 정책명을 작성해주세요.")
        return name_len
    
    @field_validator("policy_type")
    @classmethod
    def name_not_none_check(cls, type):
        if(type == None):
            raise HTTPException(status_code=400, detail="지점 정책 카테고리 작성란이 누락되었습니다. 다시 작성해주세요.")
        return type

    @field_validator("effective_from")
    @classmethod
    def effective_from_not_none_check(cls, start_date):
        if(start_date == None):
            raise HTTPException(status_code=400, detail="지점 정책 시작일란이 누락되었습니다. 다시 작성해주세요.")
        return start_date



class BranchUpdate(BaseSettings):
    name: str
    policy_type: BranchCreateEnum
    effective_to: Optional[date] = None


    @field_validator("name")
    @classmethod
    def name_none_check(cls, name):
        if(name == None):
            raise HTTPException(status_code=400, detail="지점 정책명 작성란이 누락되었습니다. 다시 작성해주세요.")
        return name
    
    @field_validator("name")
    @classmethod
    def name_len_check(cls, name_len):
        if(len(name_len.strip()) < 1):
            raise HTTPException(status_code=400, detail="2자 이상으로 지점 정책명을 작성해주세요.")
        return name_len

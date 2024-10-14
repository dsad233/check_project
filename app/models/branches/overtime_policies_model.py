from datetime import datetime

from pydantic import field_validator, Field
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Index
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from pydantic_settings import BaseSettings

from fastapi import HTTPException

class OverTimePolicies(Base): #연장근무 설정
    __tablename__ = "overtime_policies"
    # __table_args__ = (
    #     Index('idx_part_policies_branch_id', 'branch_id'),
    #     Index('idx_part_policies_branch_policy_id', 'branch_policy_id'),
    # )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)  # 예: 의사, 간호사...
    
    # 연장근무 당 지급 금액 설정
    ot_30 = Column(Integer, nullable=False)
    ot_60 = Column(Integer, nullable=False)
    ot_90 = Column(Integer, nullable=False)
    ot_120 = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_yn = Column(String(1), default="N")


class OverTimeUpdate(BaseSettings):
    name : str = Field(description="파트명")
    ot_30 : int = Field(description="O.T 30분 초과")
    ot_60 : int = Field(description="O.T 60분 초과")
    ot_90 : int = Field(description="O.T 90분 초과")
    ot_120 : int = Field(description="O.T 120분 초과")
    
    @field_validator("ot_30")
    @classmethod
    def ot_30_none_check(cls, ot_30):
        if(ot_30 == None):
            raise HTTPException(status_code= 400, detail="ot_30란이 누락되었습니다. 다시 작성해주세요.")
        return ot_30
         
    @field_validator("ot_60")
    @classmethod
    def ot_60_none_check(cls, ot_60):
        if(ot_60 == None):
             raise HTTPException(status_code= 400, detail="ot_60란이 누락되었습니다. 누락되었습니다. 다시 작성해주세요.")
        return ot_60
    
    @field_validator("ot_90")
    @classmethod
    def ot_60_none_check(cls, ot_90):
        if(ot_90 == None):
             raise HTTPException(status_code= 400, detail="ot_90란이 누락되었습니다. 다시 작성해주세요.")
        return ot_90
        
    @field_validator("ot_120")
    @classmethod
    def ot_60_none_check(cls, ot_120):
        if(ot_120 == None):
             raise HTTPException(status_code= 400, detail="ot_120란이 누락되었습니다. 다시 작성해주세요.")
        return ot_120
           

class OverTimeCreate(BaseSettings):
    name : str = Field(description="파트명")
    ot_30 : int = Field(description="O.T 30분 초과")
    ot_60 : int = Field(description="O.T 60분 초과")
    ot_90 : int = Field(description="O.T 90분 초과")
    ot_120 : int = Field(description="O.T 120분 초과")
    
    @field_validator("ot_30")
    @classmethod
    def ot_30_none_check(cls, ot_30):
        if(ot_30 == None):
            raise HTTPException(status_code= 400, detail="ot_30란이 누락되었습니다. 다시 작성해주세요.")
        return ot_30
         
    @field_validator("ot_60")
    @classmethod
    def ot_60_none_check(cls, ot_60):
        if(ot_60 == None):
             raise HTTPException(status_code= 400, detail="ot_60란이 누락되었습니다. 누락되었습니다. 다시 작성해주세요.")
        return ot_60
    
    @field_validator("ot_90")
    @classmethod
    def ot_60_none_check(cls, ot_90):
        if(ot_90 == None):
             raise HTTPException(status_code= 400, detail="ot_90란이 누락되었습니다. 다시 작성해주세요.")
        return ot_90
        
    @field_validator("ot_120")
    @classmethod
    def ot_60_none_check(cls, ot_120):
        if(ot_120 == None):
             raise HTTPException(status_code= 400, detail="ot_120란이 누락되었습니다. 다시 작성해주세요.")
        return ot_120

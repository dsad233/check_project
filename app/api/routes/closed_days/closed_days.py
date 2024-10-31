from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy import and_, func, select, extract

from app.api.routes.closed_days.dto.closed_days_response_dto import HospitalClosedDaysResponseDTO, UserClosedDayDatesResponseDTO, UserClosedDayDetailDTO
from app.core.database import get_db
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.middleware.tokenVerify import get_current_user, validate_token
from app.models.closed_days.closed_days_model import ClosedDays, ClosedDayCreate
from app.models.users.users_model import Users
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.closed_day_service import ClosedDayService

router = APIRouter()

# 휴무일 지점 다중 휴무 생성
@router.post("/{branch_id}/closed-days/arrays")
async def create_branch_arrays_closed_day(branch_id : int, token : Annotated[Users, Depends(get_current_user)], array_list: List[ClosedDayCreate] = Body(...), db: AsyncSession = Depends(get_db)):
    try:

        if token.role.strip() == "MSO 최고권한" or token.role.strip() == "최고관리자":
            pass 
        elif token.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
        
        results = []
        for data in array_list:
            new_closed_day = ClosedDays(
                branch_id=branch_id,
                closed_day_date=data.closed_day_date,
                memo=data.memo,
            )
            results.append(new_closed_day)

        db.add_all(results)
        await db.commit()

        return {
            "message": "지점 다중 휴무일이 성공적으로 생성되었습니다."
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 생성에 실패하였습니다.")

@router.get("/{branch_id}/closed-days/hospitals")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_all_closed_days(request : Request, branch_id : int, closed_day_service: ClosedDayService = Depends(ClosedDayService), year: int = datetime.now().year, month : int = datetime.now().month) -> HospitalClosedDaysResponseDTO:
    return HospitalClosedDaysResponseDTO.to_DTO(await closed_day_service.get_all_hospital_closed_days(branch_id, year, month))     

@router.get("/{branch_id}/closed-days/users")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_all_user_closed_days(request : Request, branch_id : int, closed_day_service: ClosedDayService = Depends(ClosedDayService), year: int = datetime.now().year, month : int = datetime.now().month) -> List[UserClosedDayDetailDTO]:
    return await closed_day_service.get_all_user_closed_dates(branch_id, year, month)
    
# 휴일 지점별 전체 조회 
@router.get("/{branch_id}/closed-days")
@available_higher_than(Role.EMPLOYEE)
async def get_all_closed_days(request : Request, branch_id : int, service: ClosedDayService = Depends(ClosedDayService), year: int = datetime.now().year, month : int = datetime.now().month) -> UserClosedDayDatesResponseDTO:
    '''
    지점별 전체 휴무 조회 API
    '''
    return { 
        "user_closed_days": {
            '2024-01-01' : [
                {"user_name": "박다인", "part_name": "코디", "category": "정규휴무"}, 
                {"user_name": "성동제", "part_name": "양진아", "category": "연차"}
            ], 
            '2024-01-02' : [
                {"user_name": "장석찬", "part_name": "코디", "category": "연차 종일"}, 
                {"user_name": "이다희", "part_name": "간호", "category": "연차 종일"}
            ], 
            '2024-01-03' : [
                {"user_name": "고혜솔", "part_name": "간호", "category": "조퇴"}
            ]
        }, 
        "hospital_closed_days": [
            "2024-01-01", 
            "2024-01-08", 
            "2024-01-15"
        ] 
    }
    
# 휴무일 지점 다중 삭제 [어드민만]
@router.delete("/{branch_id}/closed-days/arrays/delete")
async def delete_branch_arrays_closed_day(branch_id : int, token : Annotated[Users, Depends(get_current_user)], array_list: List[int] = Body(...), db: AsyncSession = Depends(get_db)):
    try:
        if token.role.strip() == "MSO 최고권한" or token.role.strip() == "최고관리자":
            pass 
        elif token.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
        
        for data in array_list:
            find_one_closed_days = await db.execute(select(ClosedDays).where(ClosedDays.id == data, ClosedDays.branch_id == branch_id, ClosedDays.deleted_yn == "N"))
            result = find_one_closed_days.scalar_one_or_none()

            if(result == None):
                raise HTTPException(status_code=404, detail="휴무일이 존재하지 않습니다.")

            await db.delete(result)

        await db.commit()

        return {
            "message": "지점 휴무일이 성공적으로 다중 삭제되었습니다."
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="다중 휴무일 삭제에 실패하였습니다.")
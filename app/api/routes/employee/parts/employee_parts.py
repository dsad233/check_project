from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.parts_schemas import PartResponse
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.middleware.tokenVerify import get_current_user
from app.models.parts.parts_model import Parts

router = APIRouter()


@router.get("", response_model=list[PartResponse], summary="현재 사용자의 부서 정보 조회")
@available_higher_than(Role.EMPLOYEE)
async def get_employee_part(
        context: Request,
        branch_id: int,
        session: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
) -> list[PartResponse]:
    try:
        # part_id가 없는 경우 체크
        if not current_user.part_id:
            raise HTTPException(
                status_code=400,
                detail="소속된 부서가 없습니다."
            )

        # 사원 권한 체크 추가
        if current_user.role not in [Role.EMPLOYEE]:
            raise HTTPException(
                status_code=401,
                detail="사원만 접근할 수 있는 API입니다."
            )

        # 현재 사용자의 branch_id와 요청된 branch_id가 일치하는지 확인
        if current_user.branch_id != branch_id:
            raise HTTPException(
                status_code=403,
                detail="다른 지점의 부서 정보는 조회할 수 없습니다."
            )

        # 현재 사용자의 part_id로 직접 조회
        stmt = (
            select(Parts)
            .where(
                (Parts.id == current_user.part_id) &
                (Parts.branch_id == branch_id) &
                (Parts.deleted_yn == "N")
            )
        )

        result = await session.execute(stmt)
        part = result.scalars().first()

        if not part:
            return []

        # 단일 파트 정보를 리스트로 반환
        # 모든 필수 필드를 포함하여 반환
        return [PartResponse(
            id=part.id,
            name=part.name,
            branch_id=part.branch_id,
            auto_annual_leave_grant=part.auto_annual_leave_grant,
            created_at=part.created_at,
            updated_at=part.updated_at,
            deleted_yn=part.deleted_yn,
            is_doctor=part.is_doctor,
            required_certification=part.required_certification,
            leave_granting_authority=part.leave_granting_authority
        )]

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Error in get_employee_part: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="부서 정보 조회 중 오류가 발생했습니다."
        )
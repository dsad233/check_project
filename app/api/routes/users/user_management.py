from datetime import UTC, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, logger
from sqlalchemy import select, case, func, distinct, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, aliased

from app.common.dto.response_dto import ResponseDTO
from app.core.database import get_db
from app.cruds.users.users_crud import find_all_by_branch_id_and_role
from app.dependencies.user_management import get_user_management_service
from app.enums.users import Role, UserStatus
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.users.users_model import Users, UserUpdate, RoleUpdate, UserCreate, CreatedUserDto, AdminUsersDto
from app.schemas.parts_schemas import PartRequest
from app.models.parts.parts_model import Parts
from app.models.commutes.commutes_model import Commutes
from app.models.parts.user_salary import UserSalary
from app.schemas.user_management.user_management_schemas import CurrentUserDTO, UserDTO, UserListResponseDTO
from app.dependencies.user_management import get_user_management_service
from app.service.user_management.service import UserManagementService, UserQueryService
from app.models.users.time_off_model import TimeOff

router = APIRouter()
user_query_service = UserQueryService()

class UserManagement:
    router = router

    @router.get("", response_model=UserListResponseDTO)
    async def get_users(
        page: int = Query(1, ge=1),
        record_size: int = Query(10, ge=1),
        status: Optional[UserStatus] = Query(
            None, 
            description="사용자 상태 필터링 (가능한 값: '전체' => 삭제회원제외, '재직자' => 퇴사자,휴직자 제외, '퇴사자', '휴직자', '삭제회원', 빈 값은 삭제회원 포함 전체 조회)"
        ),
        name: Optional[str] = None,
        phone: Optional[str] = None,
        branch_id: Optional[int] = None,
        part_id: Optional[int] = None,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ): 
        """
        사용자 목록을 조회합니다.
        """
        try:
            if not current_user:
                raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")

            users_data, total_count = await user_query_service.get_users_service(
                db=db,
                current_user=current_user,
                page=page,
                record_size=record_size,
                status=status,
                name=name,
                phone=phone,
                branch_id=branch_id,
                part_id=part_id
            )

            if not users_data:
                return UserListResponseDTO(
                    message="조건에 맞는 유저가 없습니다.",
                    data=[],
                    total=0,
                    count=0,
                    page=page,
                    record_size=record_size
                )

            return UserListResponseDTO(
                message="유저를 정상적으로 조회하였습니다.",
                data=users_data,
                total=total_count,
                count=len(users_data),
                page=page,
                record_size=record_size
            )

        except Exception as err:
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.post("", response_model=ResponseDTO[CreatedUserDto])
    async def create_user(
            user_create: UserCreate,
            user_management_service: UserManagementService = Depends(get_user_management_service),
            current_user: Users = Depends(get_current_user),
            session: AsyncSession = Depends(get_db)
    ):
        """
        사용자를 생성합니다.
        
        role 가능한 값: 'MSO 최고권한', '최고관리자', '통합관리자', '관리자', '사원', '퇴사자', '휴직자', '임시생성' //
        gender 가능한 값: '남자', '여자' //
        education.school_type 가능한 값: '초등학교', '중학교', '고등학교', '대학교', '대학원' //
        education.graduation_type 가능한 값: '졸업', '졸업예정', '재학중', '휴학', '중퇴' //
        career.contract_type 가능한 값: '정규직', '계약직', '인턴', '파트타임' //
        """
        created_user = await user_management_service.add_user(
            user_create=user_create,
            session=session
        )
        data = await CreatedUserDto.build(user=created_user, session=session)

        return ResponseDTO(
            status="SUCCESS",
            message="유저가 성공적으로 생성되었습니다.",
            data=data,
        )

    @router.get("/me", response_model=ResponseDTO[CurrentUserDTO])
    async def get_user(
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user)
    ):
        try:
            if not current_user:
                raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")

            user_dto = CurrentUserDTO.from_user(current_user)

            return ResponseDTO(
                status="SUCCESS",
                message="현재 로그인한 사용자를 정상적으로 조회하였습니다.",
                data=user_dto,
            )

        except Exception as err:
            logger.error("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.get("/admin", response_model=ResponseDTO[AdminUsersDto])
    async def get_admin_user(
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user)
    ):
        users = await find_all_by_branch_id_and_role(session=db, branch_id=current_user.branch_id, role=Role.ADMIN)
        if not users:
            return ResponseDTO(
                status="FAIL",
                message="조건에 맞는 유저가 없습니다.",
            )

        data = await AdminUsersDto.build(users=users)

        return ResponseDTO(
            status="SUCCESS",
            message="수퍼관리자 유저를 정상적으로 조회하였습니다.",
            data=data,
        )

    @router.get("/{id}", response_model=ResponseDTO[UserDTO])
    async def get_user_detail(
            id: int,
            user_management_service: UserManagementService = Depends(get_user_management_service),
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user)
    ):
        """
        ID를 입력 시 세부정보가 조회되며, 권한에 따른 정보 접근이 가능합니다. 세부정보는 관리자만 볼 수 있습니다.
        """
        try:
            user_dto = await user_management_service.get_user_detail(
                db=db,
                user_id=id,
                current_user=current_user
            )

            return ResponseDTO(
                status="SUCCESS",
                message="유저를 정상적으로 조회하였습니다.",
                data=user_dto,
            )
            
        except HTTPException as http_exc:
            raise http_exc
        
        except Exception as err:
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.patch("/{user_id}")
    async def update_user(
        user_id: int,
        user_update: UserUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: Users = Depends(get_current_user),
        user_management_service: UserManagementService = Depends(get_user_management_service)
    ):
        """
        유저의 세부 정보를 수정합니다.
        gender 가능한 값: '남자', '여자' //
        education.school_type 가능한 값: '초등학교', '중학교', '고등학교', '대학교', '대학원' //
        education.graduation_type 가능한 값: '졸업', '졸업예정', '재학중', '휴학', '중퇴' //
        career.contract_type 가능한 값: '정규직', '계약직', '인턴', '파트타임' //
        """
        try:
            # 서비스 레이어 호출
            await user_management_service.update_user(
                user_id=user_id,
                user_update=user_update,
                session=db,
                current_user=current_user
            )
            
            return {"message": "유저 정보가 성공적으로 업데이트되었습니다."}

        except HTTPException as http_exc:
            await db.rollback()
            raise http_exc
        except Exception as err:
            await db.rollback()
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.patch("/{id}/role")
    async def update_user_role(
            id: int,
            role_update: RoleUpdate,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user)
    ):
        """
        유저의 권한을 수정합니다. "role" : "최고관리자" 이렇게 수정합니다.
        가능한 역할: "MSO 최고권한", "최고관리자", "통합관리자", "관리자", "사원", "퇴사자", "휴직자"
        """
        try:
            user_query = select(Users).where(Users.id == id)
            result = await db.execute(user_query)
            target_user = result.scalar_one_or_none()

            if not target_user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            # if not current_user.can_edit_user(target_user):
            #     raise HTTPException(status_code=403, detail="역할을 수정할 권한이 없습니다.")

            if role_update.role not in ["MSO 최고권한", "최고관리자", "통합관리자", "관리자", "사원", "퇴사자", "휴직자"]:
                raise HTTPException(status_code=400, detail="유효하지 않은 역할입니다.")

            target_user.role = role_update.role
            await db.commit()
            return {"message": "유저의 역할이 성공적으로 업데이트되었습니다."}

        except HTTPException as http_exc:
            await db.rollback()
            raise http_exc
        except Exception as err:
            await db.rollback()
            print(f"에러가 발생하였습니다: {err}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.patch("/{id}/parts")
    async def update_user_parts(
            id: int,
            part_update: PartRequest,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user)
    ):
        """
        유저의 파트를 수정합니다. 
        "part_ids": [1, 2, 3] 형식으로 파트 ID 리스트를 전달합니다.
        """
        try:
            user_query = select(Users).options(joinedload(Users.parts)).where(Users.id == id)
            result = await db.execute(user_query)
            target_user = result.unique().scalar_one_or_none()

            if not target_user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            # if not current_user.can_edit_user(target_user):
            #     raise HTTPException(status_code=403, detail="파트를 수정할 권한이 없습니다.")

            new_parts = await db.execute(select(Parts).where(Parts.id.in_(part_update.part_ids)))
            new_parts = new_parts.scalars().all()

            if len(new_parts) != len(part_update.part_ids):
                raise HTTPException(status_code=404, detail="일부 파트 ID가 존재하지 않습니다.")

            target_user.parts = new_parts
            await db.commit()
            
            # 업데이트된 파트 정보 반환
            updated_parts = [{"id": part.id, "name": part.name} for part in target_user.parts]
            return {"message": "유저의 파트가 성공적으로 업데이트되었습니다.", "updated_parts": updated_parts}

        except HTTPException as http_exc:
            await db.rollback()
            raise http_exc
        except Exception as err:
            await db.rollback()
            print(f"에러가 발생하였습니다: {err}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.delete("/{id}")
    async def delete_user(
            id: int,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user)
    ):
        try:
            # 요청된 사용자 정보를 미리 로드
            user_query = select(Users).options(
                joinedload(Users.part),
                joinedload(Users.branch)
            ).where(Users.id == id)
            result = await db.execute(user_query)
            target_user = result.unique().scalar_one_or_none()

            if not target_user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            # 권한 체크
            # if not current_user.can_delete_user(target_user):
            #     raise HTTPException(status_code=403, detail="사용자를 삭제할 권한이 없습니다.")

            if target_user.deleted_yn == "Y":
                raise HTTPException(status_code=400, detail="이미 삭제된 유저입니다.")

            # 사용자 삭제 (soft delete)
            target_user.deleted_yn = "Y"
            target_user.updated_at = datetime.now(UTC)
            await db.commit()

            return {"message": "유저가 성공적으로 삭제되었습니다."}

        except HTTPException as http_exc:
            await db.rollback()
            raise http_exc
        except Exception as err:
            await db.rollback()
            logger.error(f"에러가 발생하였습니다: {err}")
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
        
    @router.delete("/{id}/hard-delete")
    async def hard_delete_user(
            id: int,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user)
    ):
        try:
            # 요청된 사용자 정보를 미리 로드
            user_query = select(Users).options(
                joinedload(Users.parts),
                joinedload(Users.branch)
            ).where(Users.id == id)
            result = await db.execute(user_query)
            target_user = result.unique().scalar_one_or_none()

            if not target_user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            # 권한 체크
            # if not current_user.can_delete_user(target_user):
            #     raise HTTPException(status_code=403, detail="사용자를 완전히 삭제할 권한이 없습니다.")
            
            # deleted_yn이 'Y'인 경우에만 완전 삭제 가능
            if target_user.deleted_yn != "Y":
                raise HTTPException(status_code=400, detail="소프트 삭제되지 않은 사용자는 완전히 삭제할 수 없습니다.")

            # 사용자 삭제
            await db.delete(target_user)
            await db.commit()

            return {"message": "유저가 성공적으로 완전히 삭제되었습니다."}

        except HTTPException as http_exc:
            await db.rollback()
            raise http_exc
        except Exception as err:
            await db.rollback()
            print(f"에러가 발생하였습니다: {err}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
        
    @router.patch("/{id}/restore")
    async def restore_user(
            id: int,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user)
    ):
        try:
            # 요청된 사용자 정보를 미리 로드
            user_query = select(Users).options(
                joinedload(Users.part),
                joinedload(Users.branch)
            ).where(Users.id == id)
            result = await db.execute(user_query)
            target_user = result.unique().scalar_one_or_none()

            if not target_user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            # 권한 체크 (can_delete_user 메서드 사용)
            # if not current_user.can_delete_user(target_user):
            #     raise HTTPException(status_code=403, detail="해당 사용자를 복구할 권한이 없습니다.")

            if target_user.deleted_yn == "N":
                raise HTTPException(status_code=400, detail="이미 복구된 유저입니다.")

            # 사용자 복구
            target_user.deleted_yn = "N"
            target_user.updated_at = datetime.now(UTC)
            await db.commit()

            return {"message": "유저가 성공적으로 복구되었습니다."}

        except HTTPException as http_exc:
            await db.rollback()
            raise http_exc
        except Exception as err:
            await db.rollback()
            logger.error(f"에러가 발생하였습니다: {err}")
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
        
    # @router.get("/{id}/resident-registration-number")
    # async def get_resident_registration_number(
    #         id: int,
    #         db: AsyncSession = Depends(get_db)
    # ):
    #     user_query = select(Users).where(Users.id == id)
    #     result = await db.execute(user_query)
    #     target_user = result.unique().scalar_one_or_none()

    #     if not target_user:
    #         raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

    #     return {"resident_registration_number": target_user.resident_registration_number}

user_management = UserManagement()
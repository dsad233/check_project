from datetime import UTC, datetime
from pyexpat.errors import messages
from typing import Optional, List, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy import func, select, update, case, func, distinct, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only, aliased
from sqlalchemy.util import await_only
from starlette import status

from app.common.dto.response_dto import ResponseDTO
from app.core.database import async_session, get_db
from app.cruds.users.users_crud import find_by_email, add_user, find_all_by_branch_id, find_all_by_branch_id_and_role
from app.enums.users import Role
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.users.users_model import Users, UserUpdate, RoleUpdate, UserCreate, CreatedUserDto, AdminUserDto, \
    AdminUsersDto
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts, PartUpdate
from app.models.commutes.commutes_model import Commutes
from app.models.parts.user_salary import UserSalary
from app.middleware.permission import UserPermission  

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

class UserManagement:
    router = router

    @router.get("")
    async def get_users(
        current_user: Users = Depends(get_current_user),
        page: int = Query(1, ge=1),
        record_size: int = Query(10, ge=1),
        status: Optional[str] = None, 
        name: Optional[str] = None,
        phone: Optional[str] = None,
        branch_id: Optional[int] = None,
        part_id: Optional[int] = None,
    ): 
        try:
            if not current_user:
                raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")
        
            UserAlias = aliased(Users)

            # 기본 쿼리 구성
            base_query = (
                select(UserAlias, 
                    func.max(Commutes.updated_at).label('last_activity'),
                    func.max(UserSalary.monthly_salary).label('monthly_salary'),
                    func.max(UserSalary.annual_salary).label('annual_salary'))
                .options(joinedload(UserAlias.parts), joinedload(UserAlias.branch))
                .outerjoin(Commutes, UserAlias.id == Commutes.user_id)
                .outerjoin(UserSalary, UserAlias.id == UserSalary.user_id)
                .group_by(UserAlias.id)
            )

            # 1. 사용자 역할에 따른 1차 필터링
            # query = current_user.get_accessible_users_query(base_query, UserAlias)

            query = base_query

            # 권한 체크
            # if branch_id and not current_user.can_access_branch(branch_id):
            #     return {"message": "해당 지점에 접근할 권한이 없습니다."}
            # if part_id and not current_user.can_access_parts([part_id]):
            #     return {"message": "해당 파트에 접근할 권한이 없습니다."}

            # 2. 상태 검색 조건 적용
            if status:
                if status == '퇴사자':
                    query = query.filter(UserAlias.deleted_yn == "N", UserAlias.role == "퇴사자")
                elif status == '휴직자':
                    query = query.filter(UserAlias.deleted_yn == "N", UserAlias.role == "휴직자")
                elif status == '재직자':
                    query = query.filter(UserAlias.deleted_yn == "N", ~UserAlias.role.in_(["퇴사자", "휴직자"]))
                elif status == '삭제유저':
                    query = query.filter(UserAlias.deleted_yn == "Y")

            # 3. 추가 검색 조건 적용
            if name:
                query = query.filter(UserAlias.name.ilike(f"%{name}%"))
            if phone:
                query = query.filter(UserAlias.phone_number.ilike(f"%{phone}%"))
            if branch_id:
                query = query.filter(UserAlias.branch_id == branch_id)
            if part_id:
                query = query.filter(UserAlias.parts.any(Parts.id == part_id))

            # 총 개수 계산
            count_query = select(func.count(distinct(UserAlias.id))).select_from(query.subquery())
            total_count = await db.execute(count_query)
            total_count = total_count.scalar_one()

            # 정렬 및 페이지네이션
            query = query.order_by(
                case((UserAlias.id == current_user.id, literal_column("0")), else_=literal_column("1")),
                UserAlias.id
            ).offset((page - 1) * record_size).limit(record_size)

            # 쿼리 실행
            result = await db.execute(query)
            users_data = result.unique().all()

            # 결과 처리
            user_data = []
            for user, last_activity, monthly_salary, annual_salary in users_data:
                user_dict = {
                    "id": user.id,
                    "name": user.name,
                    "gender": user.gender,
                    "email": user.email,
                    "hire_date": user.hire_date,
                    "parts": [
                        {"id": part.id, "name": part.name} for part in user.parts
                    ] if user.parts else None,
                    "branch": {
                        "id": user.branch.id,
                        "name": user.branch.name
                    } if user.branch else None,
                    "role": user.role,
                    "last_activity": last_activity
                }

                # user_dict = {
                #     "id": user.id,
                #     "branch": {
                #         "id": user.branch.id,
                #         "name": user.branch.name
                #     },
                #     "name": user.name,
                #     "work_part": user.part.name,
                #     "birth_date": user.birth_date,
                #     "phone_number": user.phone_number,
                #     "email": user.email,
                #     "hire_date": user.hire_date,
                #     "monthly_salary": monthly_salary,
                #     "annual_salary": annual_salary,
                #     # 근무 기간 추가
                #     # 계약 기간 추가
                # }

                # 전체 정보 접근 권한 확인
                # if current_user.can_access_full_user_info(user):
                #     user_dict.update({
                #         "birth_date": user.birth_date,
                #         "phone_number": user.phone_number,
                #         "retirement_date": user.retirement_date,
                #         "leave_date": user.leave_date,
                #         "monthly_salary": monthly_salary,
                #         "annual_salary": annual_salary,
                #     })

                user_dict.update({
                    "birth_date": user.birth_date,
                    "phone_number": user.phone_number,
                    # "retirement_date": user.retirement_date,
                    # "leave_date": user.leave_date,
                    "retirement_date": None,
                    "leave_date": None,
                    "monthly_salary": monthly_salary,
                    "annual_salary": annual_salary,
                })


                user_data.append(user_dict)

            if not user_data:
                return {
                    "message": "조건에 맞는 유저가 없습니다.",
                    "data": [],
                    "total": 0,
                    "page": page,
                    "record_size": record_size,
                }

            return {
                "message": "유저를 정상적으로 조회하였습니다.",
                "data": user_data,
                "total": total_count,
                "count": len(user_data),
                "page": page,
                "record_size": record_size,
            }

        except Exception as err:
            print(f"에러가 발생하였습니다: {err}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.post("", response_model=ResponseDTO[CreatedUserDto])
    async def create_user(user: UserCreate, current_user: Users = Depends(get_current_user)):
        if await find_by_email(session=db, email=user.email):
            raise HTTPException(status_code=400, detail="이미 등록된 이메일 주소입니다.")

        # TODO: 메서드를 사용하는 사용자의 권한 조회 로직 필요

        new_user = Users(**user.model_dump())
        created_user = await add_user(session=db, user=new_user)
        data = await CreatedUserDto.build(user=created_user)

        return ResponseDTO(
            status="SUCCESS",
            message="유저가 성공적으로 생성되었습니다.",
            data=data,
        )

    @router.get("/me", response_model=ResponseDTO[dict])
    async def get_user(current_user: Users = Depends(get_current_user)):
        try:
            if not current_user:
                raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")

            user_dict = {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "role": current_user.role,
                "parts": [
                    {"id": part.id, "name": part.name} for part in current_user.parts
                ] if current_user.parts else None,
                "branch": {
                    "id": current_user.branch.id,
                    "name": current_user.branch.name
                } if current_user.branch else None,
            }

            return ResponseDTO(
                status="SUCCESS",
                message="현재 로그인한 사용자를 정상적으로 조회하였습니다.",
                data=user_dict,
            )

        except Exception as err:
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.get("/admin", response_model=ResponseDTO[AdminUsersDto])
    async def get_admin_user(current_user: Users = Depends(get_current_user)):
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

    @router.get("/{id}", response_model=ResponseDTO[dict])
    async def get_user_detail(id: int, current_user: Users = Depends(get_current_user)):
        """
        ID를 입력 시 세부정보가 조회되며, 권한에 따른 정보 접근이 가능합니다. 세부정보는 관리자만 볼 수 있습니다.
        """
        try:
            if not current_user:
                raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")

            UserAlias = aliased(Users)

            # 요청된 사용자 정보 조회
            base_query = (
                select(UserAlias,
                       func.max(Commutes.updated_at).label('last_activity'),
                       func.max(UserSalary.monthly_salary).label('monthly_salary'),
                       func.max(UserSalary.annual_salary).label('annual_salary'))
                .options(joinedload(UserAlias.parts), joinedload(UserAlias.branch))
                .outerjoin(Commutes, UserAlias.id == Commutes.user_id)
                .outerjoin(UserSalary, UserAlias.id == UserSalary.user_id)
                .group_by(UserAlias.id)
                .where(UserAlias.id == id)
            )

            # 사용자 역할에 따른 쿼리 필터링
            # query = current_user.get_accessible_users_query(base_query, UserAlias)

            query = base_query

            # 쿼리 실행
            result = await db.execute(query)
            user_data = result.unique().first()

            if not user_data:
                raise HTTPException(status_code=404, detail="요청한 사용자를 찾을 수 없거나 접근 권한이 없습니다.")

            user, last_activity, monthly_salary, annual_salary = user_data

            # 기본 사용자 정보 구성
            user_dict = {
                "id": user.id,
                "name": user.name,
                "gender": user.gender,
                "email": user.email,
                "hire_date": user.hire_date,
                "parts": [
                    {"id": part.id, "name": part.name} for part in user.parts
                ] if user.parts else None,
                "branch": {
                    "id": user.branch.id,
                    "name": user.branch.name
                } if user.branch else None,
                "role": user.role,
                "last_activity": last_activity
            }


            # 전체 정보 접근 권한 확인
            # if current_user.can_access_full_user_info(user):
            #     user_dict.update({
            #         "birth_date": user.birth_date,
            #         "phone_number": user.phone_number,
            #         "retirement_date": user.retirement_date,
            #         "leave_date": user.leave_date,
            #         "monthly_salary": monthly_salary,
            #         "annual_salary": annual_salary,
            #     })

            user_dict.update({
                "birth_date": user.birth_date,
                "phone_number": user.phone_number,
                "retirement_date": None,
                "leave_date": None,
                "monthly_salary": monthly_salary,
                "annual_salary": annual_salary,
            })

            return ResponseDTO(
                status="SUCCESS",
                message="유저를 정상적으로 조회하였습니다.",
                data=user_dict,
            )
        except HTTPException as http_exc:
            raise http_exc
        except Exception as err:
            print(f"에러가 발생하였습니다: {err}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.patch("/{id}")
    async def update_user(id: int, user_update: UserUpdate, current_user: Users = Depends(get_current_user)):
        """
        유저의 세부 정보를 수정합니다.
        """
        try:
            user_query = select(Users).where(Users.id == id)
            result = await db.execute(user_query)
            target_user = result.scalar_one_or_none()

            if not target_user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            # if not current_user.can_edit_user(target_user):
            #     raise HTTPException(status_code=403, detail="해당 사용자의 정보를 수정할 권한이 없습니다.")

            update_data = user_update.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(status_code=400, detail="업데이트할 정보가 제공되지 않았습니다.")

            for key, value in update_data.items():
                setattr(target_user, key, value)

            await db.commit()
            return {"message": "유저 정보가 성공적으로 업데이트되었습니다."}

        except HTTPException as http_exc:
            await db.rollback()
            raise http_exc
        except Exception as err:
            await db.rollback()
            print(f"에러가 발생하였습니다: {err}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.patch("/{id}/role")
    async def update_user_role(id: int, role_update: RoleUpdate, current_user: Users = Depends(get_current_user)):
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
    async def update_user_parts(id: int, part_update: PartUpdate, current_user: Users = Depends(get_current_user)):
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
    async def delete_user(id: int, current_user: Users = Depends(get_current_user)):
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
            print(f"에러가 발생하였습니다: {err}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
        
    @router.delete("/{id}/hard-delete")
    async def hard_delete_user(id: int, current_user: Users = Depends(get_current_user)):
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
    async def restore_user(id: int, current_user: Users = Depends(get_current_user)):
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
            print(f"에러가 발생하였습니다: {err}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

user_management = UserManagement()
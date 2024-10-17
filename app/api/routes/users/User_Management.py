from datetime import UTC, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, update, and_, case
from sqlalchemy.orm import joinedload, load_only, contains_eager

from app.api.routes.auth.auth import hashPassword
from app.core.database import async_session
from app.middleware.tokenVerify import get_current_user_id, validate_token
from app.models.users.users_model import Users, UserUpdate, RoleUpdate
from app.models.parts.user_salary import UserSalary

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

class UserManagement:
    router = router

    @router.get("")
    async def get_users(
        current_user_id: int = Depends(get_current_user_id),
        page: int = Query(1, ge=1),
        record_size: int = Query(10, ge=1),
        search_status: Optional[str] = None, 
        search_name: Optional[str] = None,
        search_phone: Optional[str] = None,
        search_branch: Optional[str] = None,
    ):
        try:
            # 현재 사용�� 정보 조회
            current_user = await db.execute(select(Users).where(Users.id == current_user_id))
            current_user = current_user.scalar_one_or_none()
            
            if not current_user:
                raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")

            query = select(Users).options(
                joinedload(Users.salary),
                joinedload(Users.part),
                joinedload(Users.branch)
            )

            # 1. 사용자 role에 따른 필터링 (1차 필터)
            if current_user.role in ["MSO 최고권한", "최고관리자", "관리자"]:
                if current_user.role == "MSO 최고권한":
                    # 모든 지점의 유저 조회 (추가 필터링 없음)
                    pass
                elif current_user.role == "최고관리자":
                    # 본인 지점의 유저만 조회
                    query = query.filter(Users.branch_id == current_user.branch_id)
                elif current_user.role == "관리자":
                    # 본인 파트의 유저만 조회
                    if isinstance(current_user.part_id, list):
                        query = query.filter(Users.part_id.in_(current_user.part_id))
                    else:
                        query = query.filter(Users.part_id == current_user.part_id)
                
                # 2. 상태 검색 조건 적용 (2차 필터)
                if search_status:
                    if search_status == '퇴사자':
                        query = query.filter(Users.deleted_yn == "Y")
                    elif search_status == '휴직자':
                        query = query.filter(and_(Users.deleted_yn == "N", Users.role == "휴직자"))
                    elif search_status == '재직자':
                        query = query.filter(and_(Users.deleted_yn == "N", Users.role.notin_(["퇴직자", "휴직자"])))
                # 상태 검색이 없을 경우 모든 상태의 사용자 조회 (퇴직자 포함)
            else:
                # 일반 사용자, 퇴사자, 휴직자는 자기 자신만 조회
                query = query.filter(Users.id == current_user_id)

            # 3. 이름/전화번호/지점 검색 조건 적용 (3차 필터)
            if search_name:
                query = query.filter(Users.name.ilike(f"%{search_name}%"))
            if search_phone:
                query = query.filter(Users.phone_number.ilike(f"%{search_phone}%"))
            if search_branch:
                query = query.filter(Users.branch.has(name=search_branch))
            # 현재 사용자를 맨 앞으로 정렬
            query = query.order_by(
                case(
                    (Users.id == current_user_id, 0),
                    else_=1
                ),
                Users.id
            )

            total_count = await db.execute(select(func.count()).select_from(query.subquery()))
            total_count = total_count.scalar_one()

            skip = (page - 1) * record_size
            query = query.offset(skip).limit(record_size)

            result = await db.execute(query)
            users = result.unique().scalars().all()

            user_data = []
            for user in users:
                user_dict = {
                    "id": user.id,
                    "name": user.name,
                    "birth_date": user.birth_date,
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "hire_date": user.hire_date,
                    "monthly_salary": user.salary.monthly_salary if user.salary else None,
                    "annual_salary": user.salary.annual_salary if user.salary else None,
                    "part": user.part.name if user.part else None,
                    "branch": user.branch.name if user.branch else None,
                }
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
                "page": page,
                "record_size": record_size,
            }
        except Exception as err:
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.get("/me")
    async def get_current_user(current_user_id: int = Depends(get_current_user_id)):
        try:
            stmt = (
                select(Users)
                .options(
                    load_only(
                        Users.id, Users.name, Users.email, Users.phone_number,
                        Users.address, Users.education, Users.birth_date,
                        Users.hire_date, Users.resignation_date, Users.gender,
                        Users.part_id, Users.branch_id, Users.role,
                        Users.last_company, Users.last_position,
                        Users.last_career_start_date, Users.last_career_end_date,
                        Users.created_at, Users.updated_at, Users.deleted_yn,
                    ),
                    joinedload(Users.part),
                    joinedload(Users.branch),
                )
                .where((Users.id == current_user_id) & (Users.deleted_yn == "N"))
            )

            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            return {
                "message": "현재 로그인한 사용자를 정상적으로 조회하였습니다.",
                "data": user,
            }
        except Exception as err:
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.get("/{id}")
    async def get_user_detail(id: int, current_user_id: int = Depends(get_current_user_id)):
        try:
            # 현재 사용자 정보 조회
            current_user = await db.execute(select(Users).where(Users.id == current_user_id))
            current_user = current_user.scalar_one_or_none()
            
            if not current_user:
                raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")

            # 먼저 요청된 사용자가 존재하는지 확인
            user_exists = await db.execute(select(Users.id).where(Users.id == id))
            if not user_exists.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            stmt = (
                select(Users)
                .options(
                    load_only(
                        Users.id, Users.name, Users.email, Users.phone_number,
                        Users.address, Users.education, Users.birth_date,
                        Users.hire_date, Users.resignation_date, Users.gender,
                        Users.part_id, Users.branch_id, Users.role,
                        Users.last_company, Users.last_position,
                        Users.last_career_start_date, Users.last_career_end_date,
                        Users.created_at, Users.updated_at, Users.deleted_yn,
                    ),
                    joinedload(Users.part),
                    joinedload(Users.branch),
                )
                .where((Users.id == id) & (Users.deleted_yn == "N"))
            )

            # 권한에 따른 필터링
            if current_user.role == "MSO 최고권한":
                pass  # 모든 사용자에 접근 가능
            elif current_user.role == "최고관리자":
                stmt = stmt.filter(Users.branch_id == current_user.branch_id)
            elif current_user.role == "관리자":
                if isinstance(current_user.part_id, list):
                    stmt = stmt.filter(Users.part_id.in_(current_user.part_id))
                else:
                    stmt = stmt.filter(Users.part_id == current_user.part_id)
            else:
                # 일반 사용자는 자신의 정보만 볼 수 있음
                if current_user.id != id:
                    raise HTTPException(status_code=403, detail="해당 사용자의 정보를 조회할 권한이 없습니다.")

            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=403, detail="해당 사용자의 정보를 조회할 권한이 없습니다.")

            return {
                "message": "유저 상세 정보를 정상적으로 조회하였습니다.",
                "data": user,
            }
        except HTTPException as http_err:
            raise http_err
        except Exception as err:
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.patch("/{id}")
    async def update_user(id: int, user_update: UserUpdate, current_user_id: int = Depends(get_current_user_id)):
        try:
            # 현재 사용자 정보 조회
            current_user = await db.execute(select(Users).where(Users.id == current_user_id))
            current_user = current_user.scalar_one_or_none()
            
            if not current_user:
                raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")

            # 먼저 요청된 사용자가 존재하는지 확인
            user_exists = await db.execute(select(Users.id).where(Users.id == id))
            if not user_exists.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            update_data = user_update.model_dump(exclude_unset=True)

            if not update_data:
                raise HTTPException(status_code=400, detail="업데이트할 정보가 제공되지 않았습니다.")

            stmt = select(Users).where((Users.id == id) & (Users.deleted_yn == "N"))
            
            # 권한에 따른 필터링
            if current_user.role == "MSO 최고권한":
                pass  # 모든 사용자 정보 수정 가능
            elif current_user.role == "최고관리자":
                stmt = stmt.filter(Users.branch_id == current_user.branch_id)
            elif current_user.role == "관리자":
                if isinstance(current_user.part_id, list):
                    stmt = stmt.filter(Users.part_id.in_(current_user.part_id))
                else:
                    stmt = stmt.filter(Users.part_id == current_user.part_id)
            else:
                # 일반 사용자는 자신의 정보만 수정 가능
                if current_user.id != id:
                    raise HTTPException(status_code=403, detail="해당 사용자의 정보를 수정할 권한이 없습니다.")

            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=403, detail="해당 사용자의 정보를 수정할 권한이 없습니다.")

            update_stmt = update(Users).where(Users.id == id).values(**update_data)
            await db.execute(update_stmt)
            await db.commit()

            return {"message": "유저 정보가 성공적으로 업데이트되었습니다."}
        except HTTPException as http_err:
            await db.rollback()
            raise http_err
        except Exception as err:
            await db.rollback()
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.delete("/{id}")
    async def delete_user(id: int, current_user_id: int = Depends(get_current_user_id)):
        try:
            # 현재 사용자 정보 조회
            current_user = await db.execute(select(Users).where(Users.id == current_user_id))
            current_user = current_user.scalar_one_or_none()
            
            if not current_user:
                raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")

            # 먼저 요청된 사용자가 존재하는지 확인
            user_exists = await db.execute(select(Users.id).where(Users.id == id))
            if not user_exists.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            # 권한 확인
            if current_user.role not in ["MSO 최고권한", "최고관리자"]:
                raise HTTPException(status_code=403, detail="사용자를 삭제할 권한이 없습니다.")

            stmt = select(Users).where(Users.id == id)
            
            # 권한에 따른 필터링
            if current_user.role == "최고관리자":
                stmt = stmt.filter(Users.branch_id == current_user.branch_id)

            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=403, detail="해당 사용자를 삭제할 권한이 없습니다.")

            if user.deleted_yn == "Y":
                raise HTTPException(status_code=400, detail="이미 삭제된 유저입니다.")

            update_stmt = (
                update(Users)
                .where(Users.id == id)
                .values(deleted_yn="Y", updated_at=datetime.now(UTC))
            )
            await db.execute(update_stmt)
            await db.commit()

            return {"message": "유저가 성공적으로 삭제되었습니다."}
        except HTTPException as http_err:
            await db.rollback()
            raise http_err
        except Exception as err:
            await db.rollback()
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.patch("/{id}/role")
    async def update_user_role(id: int, role_update: RoleUpdate, current_user_id: int = Depends(get_current_user_id)):
        try:
            # 현재 사용자 정보 조회
            current_user = await db.execute(select(Users).where(Users.id == current_user_id))
            current_user = current_user.scalar_one_or_none()
            
            if not current_user:
                raise HTTPException(status_code=404, detail="현재 사용자 정보를 찾을 수 없습니다.")

            # 대상 사용자 정보 조회
            target_user = await db.execute(select(Users).where(Users.id == id))
            target_user = target_user.scalar_one_or_none()

            if not target_user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            # 역할 계층 정의
            role_hierarchy = {
                "MSO 최고권한": 3,
                "최고관리자": 2,
                "관리자": 1,
                "사원": 0
            }

            # 현재 사용자의 역할 레벨
            current_user_level = role_hierarchy.get(current_user.role, 0)
            # 대상 사용자의 현재 역할 레벨
            target_user_current_level = role_hierarchy.get(target_user.role, 0)
            # 변경하려는 역할 레벨
            new_role_level = role_hierarchy.get(role_update.role, 0)

            # 권한 확인 및 역할 변경 로직
            if current_user.role == "MSO 최고권한":
                if new_role_level >= current_user_level:
                    raise HTTPException(status_code=403, detail="자신과 같거나 더 높은 권한으로 변경할 수 없습니다.")
            elif current_user.role == "최고관리자":
                if new_role_level >= current_user_level or target_user_current_level >= current_user_level:
                    raise HTTPException(status_code=403, detail="관리자 이상의 권한으로 변경하거나, 자신과 같거나 더 높은 권한을 가진 사용자의 역할을 변경할 수 없습니다.")
                if target_user.branch_id != current_user.branch_id:
                    raise HTTPException(status_code=403, detail="다른 지점의 사용자 역할을 변경할 수 없습니다.")
            else:
                raise HTTPException(status_code=403, detail="사용자 권한을 변경할 권한이 없습니다.")

            # 역할 업데이트
            update_stmt = update(Users).where(Users.id == id).values(role=role_update.role)
            await db.execute(update_stmt)
            await db.commit()

            return {"message": "유저 권한이 성공적으로 변경되었습니다."}
        except HTTPException as http_err:
            await db.rollback()
            raise http_err
        except Exception as err:
            await db.rollback()
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

user_management = UserManagement()

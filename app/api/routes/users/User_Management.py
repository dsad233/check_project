from datetime import UTC, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, update
from sqlalchemy.orm import joinedload, load_only

from app.api.routes.auth.auth import hashPassword
from app.api.routes.users.schema.userschema import UserUpdate, UserCreate, RoleUpdate
from app.core.database import async_session
from app.middleware.tokenVerify import get_current_user_id, validate_token
from app.models.users.users_model import Users

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

class UserManagement:
    router = router

    @router.get("")
    async def get_users(
        page: int = Query(1, ge=1),
        record_size: int = Query(10, ge=1),
        search: Optional[str] = None,
        role: Optional[str] = None,
        part_id: Optional[int] = None,
        branch_id: Optional[int] = None,
        hire_date_from: Optional[datetime] = None,
        hire_date_to: Optional[datetime] = None
    ):
        try:
            query = select(Users).where(Users.deleted_yn == "N")

            if search:
                query = query.filter(
                    (Users.name.ilike(f"%{search}%")) |
                    (Users.email.ilike(f"%{search}%")) |
                    (Users.phone_number.ilike(f"%{search}%"))
                )

            if role:
                query = query.filter(Users.role == role)
            if part_id:
                query = query.filter(Users.part_id == part_id)
            if branch_id:
                query = query.filter(Users.branch_id == branch_id)
            if hire_date_from:
                query = query.filter(Users.hire_date >= hire_date_from)
            if hire_date_to:
                query = query.filter(Users.hire_date <= hire_date_to)

            total_count = await db.execute(select(func.count()).select_from(query.subquery()))
            total_count = total_count.scalar_one()

            skip = (page - 1) * record_size
            query = query.order_by(Users.id).offset(skip).limit(record_size)

            result = await db.execute(query.options(
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
            ))
            users = result.scalars().all()

            return {
                "message": "유저를 정상적으로 조회하였습니다.",
                "data": users,
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
    async def get_user_detail(id: int):
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
                .where((Users.id == id) & (Users.deleted_yn == "N"))
            )

            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            return {
                "message": "유저 상세 정보를 정상적으로 조회하였습니다.",
                "data": user,
            }
        except Exception as err:
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.patch("/{id}")
    async def update_user(id: int, user_update: UserUpdate):
        try:
            update_data = user_update.model_dump(exclude_unset=True)

            if not update_data:
                raise HTTPException(status_code=400, detail="업데이트할 정보가 제공되지 않았습니다.")

            stmt = select(Users).where((Users.id == id) & (Users.deleted_yn == "N"))
            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            update_stmt = update(Users).where(Users.id == id).values(**update_data)
            await db.execute(update_stmt)
            await db.commit()

            return {"message": "유저 정보가 성공적으로 업데이트되었습니다."}
        except Exception as err:
            await db.rollback()
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.delete("/{id}")
    async def delete_user(id: int):
        try:
            stmt = select(Users).where(Users.id == id)
            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

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
        except Exception as err:
            await db.rollback()
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.get("/resigned")
    async def get_resigned_users(
        page: int = Query(1, ge=1),
        record_size: int = Query(10, ge=1)
    ):
        try:
            query = select(Users).where(Users.deleted_yn == "Y")

            total_count = await db.execute(select(func.count()).select_from(query.subquery()))
            total_count = total_count.scalar_one()

            skip = (page - 1) * record_size
            query = query.order_by(Users.id).offset(skip).limit(record_size)

            result = await db.execute(query.options(
                load_only(
                    Users.id, Users.name, Users.email, Users.phone_number,
                    Users.resignation_date, Users.role, Users.part_id, Users.branch_id,
                ),
                joinedload(Users.part),
                joinedload(Users.branch),
            ))
            users = result.scalars().all()

            if not users:
                raise HTTPException(status_code=404, detail="퇴사자가 존재하지 않습니다.")

            return {
                "message": "퇴사자를 정상적으로 조회하였습니다.",
                "data": users,
                "total": total_count,
                "page": page,
                "record_size": record_size,
            }
        except Exception as err:
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.post("")
    async def create_user(user_create: UserCreate):
        try:
            new_user = Users(**user_create.model_dump())
            new_user.password = hashPassword(user_create.password)
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            return {
                "message": "유저가 성공적으로 생성되었습니다.",
                "data": new_user
            }
        except Exception as err:
            await db.rollback()
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    @router.patch("/{id}/role")
    async def update_user_role(id: int, role_update: RoleUpdate):
        try:
            stmt = update(Users).where(Users.id == id).values(role=role_update.role)
            result = await db.execute(stmt)
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="해당 ID의 유저가 존재하지 않습니다.")

            await db.commit()

            return {"message": "유저 권한이 성공적으로 변경되었습니다."}
        except Exception as err:
            await db.rollback()
            print("에러가 발생하였습니다.", err)
            raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

user_management = UserManagement()

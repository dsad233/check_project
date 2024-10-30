from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from app.api.routes.auth.auth import hashPassword
from app.core.database import get_db
from app.middleware.tokenVerify import get_current_user_id, validate_token, get_current_user
from app.models.users.users_model import Users, UserUpdate
from app.models.branches.branches_model import Branches
from typing import Annotated

router = APIRouter(dependencies=[Depends(validate_token)])
# db = async_session()

##
# 유저 전체 조회
@router.get("")
async def get_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    try:
        # 전체 사용자 수 조회
        count_query = (
            select(func.count()).select_from(Users).where(Users.deleted_yn == "N")
        )
        total_count = await db.execute(count_query)
        total_count = total_count.scalar_one()

        # password를 제외한 모든 컬럼 선택
        stmt = (
            select(Users)
            .options(
                load_only(
                    Users.id,
                    Users.name,
                    Users.email,
                    Users.phone_number,
                    Users.address,
                    Users.education,
                    Users.birth_date,
                    Users.hire_date,
                    Users.resignation_date,
                    Users.gender,
                    Users.part_id,
                    Users.branch_id,
                    Users.role,
                    Users.last_company,
                    Users.last_position,
                    Users.last_career_start_date,
                    Users.last_career_end_date,
                    Users.created_at,
                    Users.updated_at,
                    Users.deleted_yn,
                ),
                joinedload(Users.part),
                joinedload(Users.branch),
            )
            .where(Users.deleted_yn == "N")
            .order_by(Users.id)
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        users = result.scalars().all()

        if not users:
            raise HTTPException(status_code=404, detail="유저가 존재하지 않습니다.")

        return {
            "message": "유저를 정상적으로 전체 조회를 완료하였습니다.",
            "data": users,
            "total": total_count,
            "skip": skip,
            "limit": limit,
        }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 현재 로그인한 사용자 조회
@router.get("/me")
async def get_current_me_user(
        db: AsyncSession = Depends(get_db),
        current_user_id: int = Depends(get_current_user_id)
):
    try:
        # password를 제외한 모든 컬럼 선택
        stmt = (
            select(Users)
            .options(
                load_only(
                    Users.id,
                    Users.name,
                    Users.email,
                    Users.phone_number,
                    Users.address,
                    Users.education,
                    Users.birth_date,
                    Users.hire_date,
                    Users.resignation_date,
                    Users.gender,
                    Users.part_id,
                    Users.branch_id,
                    Users.last_company,
                    Users.last_position,
                    Users.last_career_start_date,
                    Users.last_career_end_date,
                    Users.role,
                    Users.created_at,
                    Users.updated_at,
                    Users.deleted_yn,
                ),
                joinedload(Users.part),
                joinedload(Users.branch),
            )
            .where((Users.id == current_user_id) & (Users.deleted_yn == "N"))
        )

        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=404, detail="해당 ID의 유저가 존재하지 않습니다."
            )

        return {
            "message": "현재 로그인한 사용자를 정상적으로 조회하였습니다.",
            "data": user,
        }
    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
    


# 유저 상세 조회
@router.get("/{id}")
async def get_user_detail(
        id: int,
        db: AsyncSession = Depends(get_db)
):
    try:
        # password를 제외한 모든 컬럼 선택
        stmt = (
            select(Users)
            .options(
                load_only(
                    Users.id,
                    Users.name,
                    Users.email,
                    Users.phone_number,
                    Users.address,
                    Users.education,
                    Users.birth_date,
                    Users.hire_date,
                    Users.resignation_date,
                    Users.gender,
                    Users.part_id,
                    Users.branch_id,
                    Users.last_company,
                    Users.last_position,
                    Users.last_career_start_date,
                    Users.last_career_end_date,
                    Users.created_at,
                    Users.updated_at,
                    Users.deleted_yn,
                    Users.role,
                ),
                joinedload(Users.part),
                joinedload(Users.branch),
            )
            .where((Users.id == id) & (Users.deleted_yn == "N"))
        )

        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=404, detail="해당 ID의 유저가 존재하지 않습니다."
            )

        return {
            "message": "유저 상세 정보를 정상적으로 조회하였습니다.",
            "data": user,
        }
    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 유저 정보 수정
@router.patch("/{id}")
async def update_user(
        id: int,
        user_update: UserUpdate,
        db: AsyncSession = Depends(get_db)
):
    try:
        # 업데이트할 필드만 선택
        update_data = user_update.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=400, detail="업데이트할 정보가 제공되지 않았습니다."
            )

        # 유저 존재 여부 확인
        stmt = select(Users).where((Users.id == id) & (Users.deleted_yn == "N"))
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=404, detail="해당 ID의 유저가 존재하지 않습니다."
            )

        # 유저 정보 업데이트
        update_stmt = update(Users).where(Users.id == id).values(**update_data)
        await db.execute(update_stmt)
        await db.commit()

        return {
            "message": "유저 정보가 성공적으로 업데이트되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 유저 삭제 (soft delete)
@router.delete("/{id}")
async def delete_user(
        id: int,
        db: AsyncSession = Depends(get_db)
):
    try:
        # 유저 존재 여부 확인
        stmt = select(Users).where(Users.id == id)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=404, detail="해당 ID의 유저가 존재하지 않습니다."
            )

        if user.deleted_yn == "Y":
            raise HTTPException(status_code=400, detail="이미 삭제된 유저입니다.")

        # 유저 정보 soft delete
        update_stmt = (
            update(Users)
            .where(Users.id == id)
            .values(deleted_yn="Y", updated_at=datetime.now(UTC))
        )
        await db.execute(update_stmt)
        await db.commit()

        return {
            "message": "유저가 성공적으로 삭제되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

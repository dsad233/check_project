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

router = APIRouter()

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
                    # Users.education,
                    Users.birth_date,
                    Users.hire_date,
                    Users.resignation_date,
                    Users.gender,
                    Users.part_id,
                    Users.branch_id,
                    # Users.last_company,
                    # Users.last_position,
                    # Users.last_career_start_date,
                    # Users.last_career_end_date,
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



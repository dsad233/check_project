import asyncio
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.core.database import async_session
from app.middleware.tokenVerify import get_current_user_id, validate_token
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import PartCreate, PartResponse, Parts, PartUpdate
from app.models.users.users_model import Users
from app.core.database import get_db

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


@router.get("", response_model=list[PartResponse])
async def getParts(branch_id: int, current_user_id: int = Depends(get_current_user_id)):
    try:
        user_query = select(Users).where(
            Users.id == current_user_id, Users.deleted_yn == "N"
        )
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user.role.strip() not in ["MSO 최고권한", "최고관리자", "통합관리자"] or (
            user.role.strip() == "최고관리자" and user.branch_id != branch_id
        ) or (
            user.role.strip() == "통합관리자" and user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        query = select(Parts).where(
            Parts.branch_id == branch_id, Parts.deleted_yn == "N"
        )
        result = await db.execute(query)
        parts = result.scalars().all()

        parts_dtos = []

        for part in parts:
            dto = PartResponse.model_validate(part)
            parts_dtos.append(dto)

        return parts_dtos
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

# 세마포어를 사용하여 동시 접근 제어
semaphore = asyncio.Semaphore(1)

@router.post("")
async def createPart(
    branch_id: int,
    part_create: PartCreate,
    current_user_id: int = Depends(get_current_user_id),
):
    async with semaphore:  # 세마포어를 사용하여 동시 접근 제어
        try:
            # 사용자 검증
            user_result = await db.execute(
                select(Users)
                .where(Users.id == current_user_id, Users.deleted_yn == "N")
            )
            user = user_result.scalar_one_or_none()

            if not user:
                raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

            if user.role.strip() not in ["MSO 최고권한", "최고관리자", "통합관리자"] or (
                user.role.strip() == "최고관리자" and user.branch_id != branch_id
            ) or (
                user.role.strip() == "통합관리자" and user.branch_id != branch_id
            ):
                raise HTTPException(status_code=403, detail="Not enough permissions")

            # 지점 검증
            branch_result = await db.execute(
                select(Branches)
                .where(Branches.id == branch_id, Branches.deleted_yn == "N")
            )
            branch = branch_result.scalar_one_or_none()

            if not branch:
                raise HTTPException(status_code=400, detail="존재하지 않는 지점입니다.")

            # 중복 검사
            existing_part = await db.execute(
                select(Parts)
                .where(
                    Parts.name == part_create.name,
                    Parts.branch_id == branch_id,
                    Parts.deleted_yn == "N"
                )
            )

            if existing_part.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="이미 존재하는 부서입니다.")

            # 부서 생성
            new_part = Parts(
                branch_id=branch_id,
                **part_create.model_dump(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            try:
                db.add(new_part)
                await db.commit()
                return {"message": "부서 생성에 성공하였습니다.", "status": "success"}
            
            except IntegrityError as ie:
                await db.rollback()
                return {"message": "이미 존재하는 부서입니다.", "status": "error"}

        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail="이미 존재하는 부서입니다.")
            
        except Exception as e:
            await db.rollback()
            print(f"Error in createPart: {str(e)}")  # 로깅 추가
            raise HTTPException(status_code=400, detail=str(e))

        finally:
            # 세션 정리
            await db.close()


@router.delete("/{part_id}")
async def deletePart(
    branch_id: int, part_id: int, current_user_id: int = Depends(get_current_user_id)
):
    try:
        user_query = select(Users).where(
            Users.id == current_user_id, Users.deleted_yn == "N"
        )
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user.role.strip() not in ["MSO 최고권한", "최고관리자", "통합관리자"] or (
            user.role.strip() == "최고관리자" and user.branch_id != branch_id
        ) or (
            user.role.strip() == "통합관리자" and user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        query = select(Parts).where(
            (Parts.id == part_id)
            & (Parts.branch_id == branch_id)
            & (Parts.deleted_yn == "N")
        )
        result = await db.execute(query)
        part = result.scalar_one_or_none()

        if not part:
            raise HTTPException(status_code=400, detail="존재하지 않는 부서입니다.")

        part.deleted_yn = "Y"
        await db.commit()
        return {"message": "부서 삭제에 성공하였습니다."}
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.patch("/{part_id}")
async def updatePart(
    branch_id: int,
    part_id: int,
    part_update: PartUpdate,
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        user_query = select(Users).where(
            Users.id == current_user_id, Users.deleted_yn == "N"
        )
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user.role.strip() not in ["MSO 최고권한", "최고관리자", "통합관리자"] or (
            user.role.strip() == "최고관리자" and user.branch_id != branch_id
        ) or (
            user.role.strip() == "통합관리자" and user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        query = select(Parts).where(
            (Parts.id == part_id)
            & (Parts.deleted_yn == "N")
            & (Parts.branch_id == branch_id)
        )
        result = await db.execute(query)
        part = result.scalar_one_or_none()

        if not part:
            raise HTTPException(status_code=400, detail="존재하지 않는 부서입니다.")

        if part_update.name and part_update.name != part.name:
            part_query = select(Parts).where(
                (Parts.name == part_update.name)
                & (Parts.branch_id == branch_id)
                & (Parts.deleted_yn == "N")
                & (Parts.id != part_id)  # 현재 부서 제외
            )
            part_result = await db.execute(part_query)
            part_exist = part_result.scalar_one_or_none()

            if part_exist:
                raise HTTPException(status_code=400, detail="이미 존재하는 부서입니다.")

        if part_update.name:
            part.name = part_update.name
        if part_update.task:
            part.task = part_update.task
        if part_update.is_doctor is not None:
            part.is_doctor = part_update.is_doctor
        if part_update.required_certification:
            part.required_certification = part_update.required_certification

        await db.commit()
        return {"message": "부서 수정에 성공하였습니다."}
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.api.routes.parts.schema.parts_schema import PartCreate, PartResponse
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.models.models import Branches, Parts, Users

router = APIRouter(dependencies=[Depends(validate_token)])
part_session = async_session()


@router.get("")
async def getParts(branch_id: int, current_user: Users = Depends(validate_token)):
    try:
        if current_user.role.strip() not in ["MSO 최고권한", "최고관리자"] or (
            current_user.role.strip() == "최고관리자"
            and current_user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        query = select(Parts).where(
            Parts.branch_id == branch_id, Parts.deleted_yn == "N"
        )
        result = await part_session.execute(query)
        parts = result.scalars().all()

        parts_dtos = []

        for part in parts:
            dto = PartResponse(
                id=part.id,
                name=part.name,
                task=part.task,
                is_doctor=part.is_doctor,
                required_certification=part.required_certification,
                leave_granting_authority=part.leave_granting_authority,
            )
            parts_dtos.append(dto)

        return {"message": "부서 조회에 성공하였습니다.", "data": parts_dtos}
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")


@router.post("")
async def createPart(
    branch_id: int,
    part_create: PartCreate,
    current_user: Users = Depends(validate_token),
):
    try:
        if current_user.role.strip() not in ["MSO 최고권한", "최고관리자"] or (
            current_user.role.strip() == "최고관리자"
            and current_user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        branch_query = select(Branches).where(Branches.id == branch_id)
        branch_result = await part_session.execute(branch_query)
        branch = branch_result.scalars().first()

        if not branch:
            raise HTTPException(status_code=400, detail="존재하지 않는 지점입니다.")

        part_query = select(Parts).where(
            (Parts.name == part_create.name)
            & (Parts.branch_id == branch_id)
            & (Parts.deleted_yn == "N")
        )
        part_result = await part_session.execute(part_query)
        part_exist = part_result.scalars().first()

        if part_exist:
            raise HTTPException(status_code=400, detail="이미 존재하는 부서입니다.")

        create = Parts(
            name=part_create.name,
            branch_id=branch_id,
            task=part_create.task,
            is_doctor=part_create.is_doctor,
            required_certification=part_create.required_certification,
            leave_granting_authority=part_create.leave_granting_authority,
        )
        part_session.add(create)
        await part_session.commit()

        return {"message": "부서 생성에 성공하였습니다."}
    except Exception as err:
        await part_session.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")


@router.delete("/{part_id}")
async def deletePart(
    branch_id: int, part_id: int, current_user: Users = Depends(validate_token)
):
    try:
        if current_user.role.strip() not in ["MSO 최고권한", "최고관리자"] or (
            current_user.role.strip() == "최고관리자"
            and current_user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        query = select(Parts).where(
            (Parts.id == part_id)
            & (Parts.branch_id == branch_id)
            & (Parts.deleted_yn == "N")
        )
        result = await part_session.execute(query)
        part = result.scalars().first()

        if not part:
            raise HTTPException(status_code=400, detail="존재하지 않는 부서입니다.")

        part.deleted_yn = "Y"
        await part_session.commit()
        return {"message": "부서 삭제에 성공하였습니다."}
    except Exception as err:
        await part_session.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")


@router.patch("/{part_id}")
async def updatePart(
    branch_id: int,
    part_id: int,
    part_update: PartCreate,
    current_user: Users = Depends(validate_token),
):
    try:
        if current_user.role.strip() not in ["MSO 최고권한", "최고관리자"] or (
            current_user.role.strip() == "최고관리자"
            and current_user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        query = select(Parts).where(
            (Parts.id == part_id)
            & (Parts.deleted_yn == "N")
            & (Parts.branch_id == branch_id)
        )
        result = await part_session.execute(query)
        part = result.scalars().first()

        if not part:
            raise HTTPException(status_code=400, detail="존재하지 않는 부서입니다.")

        part_query = select(Parts).where(
            (Parts.name == part_update.name)
            & (Parts.branch_id == branch_id)
            & (Parts.deleted_yn == "N")
        )
        part_result = await part_session.execute(part_query)
        part_exist = part_result.scalars().first()

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
        if part_update.leave_granting_authority:
            part.leave_granting_authority = part_update.leave_granting_authority

        await part_session.commit()
        return {"message": "부서 수정에 성공하였습니다."}
    except Exception as err:
        await part_session.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")

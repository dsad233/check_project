from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.api.routes.parts.schema.parts_schema import PartCreate, PartResponse
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.models.models import Branches, Parts, Users

router = APIRouter(dependencies=[Depends(validate_token)])
part_session = async_session()


@router.get("")
async def getParts(current_user: Users = Depends(validate_token)):
    try:
        # if current_user.role.name != 'MSO 최고권한' and current_user.role.name != '최고관리자':
        #     raise HTTPException(status_code=403, detail="권한이 없습니다.")

        query = select(Parts).where(
            Parts.branch_id == current_user.branch_id, Parts.deleted_yn == "N"
        )
        result = await part_session.execute(query)
        parts = result.scalars().all()

        parts_dtos = []

        for part in parts:
            dto = PartResponse(
                id=part.id,
                name=part.name,
            )
            parts_dtos.append(dto)

        return {"message": "부서 조회에 성공하였습니다.", "data": parts_dtos}
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")


@router.post("")
async def createPart(
    part_create: PartCreate, current_user: Users = Depends(validate_token)
):
    try:
        # if current_user.role.name != 'MSO 최고권한' and current_user.role.name != '최고관리자' and current_user.branch_id != part_create.branch_id:
        #     raise HTTPException(status_code=403, detail="권한이 없습니다.")

        branch_query = select(Branches).where(Branches.id == part_create.branch_id)
        branch_result = await part_session.execute(branch_query)
        branch = branch_result.scalars().first()

        if not branch:
            raise HTTPException(status_code=400, detail="존재하지 않는 지점입니다.")

        part_query = select(Parts).where(Parts.name == part_create.name)
        part_result = await part_session.execute(part_query)
        part_exist = part_result.scalars().first()

        if part_exist:
            raise HTTPException(status_code=400, detail="이미 존재하는 부서입니다.")

        create = Parts(
            name=part_create.name,
            branch_id=part_create.branch_id,
        )
        part_session.add(create)
        await part_session.commit()

        return {"message": "부서 생성에 성공하였습니다."}
    except Exception as err:
        await part_session.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다")


@router.delete("/{part_id}")
async def deletePart(part_id: int, current_user: Users = Depends(validate_token)):
    try:
        # if current_user.role.name != 'MSO 최고권한' and current_user.role.name != '최고관리자' and current_user.branch_id != part_create.branch_id:
        #     raise HTTPException(status_code=403, detail="권한이 없습니다.")

        query = select(Parts).where(Parts.id == part_id, Parts.deleted_yn == "N")
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

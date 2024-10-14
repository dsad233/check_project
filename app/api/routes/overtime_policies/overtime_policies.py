from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.future import select

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.models.branches.overtime_policies_model import OverTimePolicies, OverTimeCreate, OverTimeUpdate
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts

# from app.api.routes.overtimes.schema.overtimeschema import OverTimeCrete, OverTimeEdit

router = APIRouter(dependencies=[Depends(validate_token)])
overtime = async_session()


# overtime 전체 조회
@router.get("/{branch_id}/overtime_policies")
async def find_overtime_all(branch_id : int):
    try:
        overtime_all = await overtime.execute(select(OverTimePolicies).where(OverTimePolicies.branch_id == branch_id, OverTimePolicies.deleted_yn == "N").offset(0).limit(100))
        result = overtime_all.scalars().all()

        if len(overtime_all) == 0:
            return JSONResponse(
                status_code=404, content="오버타임 정책들이 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 오버타임 정책 전체 조회에 성공하였습니다.",
            "data": result
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail="오버타임 정책 전체 조회에 에러가 발생하였습니다.")

# overtime 상세 조회
@router.get("/{branch_id}/overtime_policies/{id}")
async def find_overtime_one (branch_id : int, id : int):
    try:
        overtime_one = await overtime.execute(select(OverTimePolicies).where(OverTimePolicies.branch_id == branch_id, OverTimePolicies.id == id, OverTimePolicies.deleted_yn == "N"))
        result = overtime_one.scalar_one_or_none()

        if result == None:
            raise HTTPException(status_code=404, detail="오버타임 정책이 존재하지 않습니다.")
        
        return {
            "message": "성공적으로 오버타임 정책 상세 조회에 성공하였습니다.",
            "data": result
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail="오버타임 정책 상세 조회에 에러가 발생하였습니다.")


# overtime 파트명별 검색 조회
@router.get("/{branch_id}/overtime_policies/part_name/{name}")
async def find_overtime_one (branch_id : int, name : str):
    try:
        overtime_one = await overtime.execute(select(OverTimePolicies).where(OverTimePolicies.branch_id == branch_id, Parts.name.like(f"{name}%"), OverTimePolicies.deleted_yn == "N"))
        result = overtime_one.scalar_one_or_none()

        if result == None:
            raise HTTPException(status_code=404, detail="오버타임 정책이 존재하지 않습니다.")
        
        return {
            "message": "성공적으로 오버타임 정책 파트명 조회에 성공하였습니다.",
            "data": result
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail="오버타임 정책 파트명별 조회에 에러가 발생하였습니다.")

    

# overtime 지점명에 따라 조회
@router.get("/{branch_id}/overtime_policies/branches/{name}")
async def find_spot(branch_id : int, name : str):
    try:
        find_spot = await overtime.execute(
            select(OverTimePolicies).where(Branches.name.like(f"{name}%"), OverTimePolicies.branch_id == branch_id, OverTimePolicies.deleted_yn == "N")
        )
        result = find_spot.scalar_one_or_none()

        if result == None:
            raise HTTPException(status_code=404, detail="오버타임 정책이 존재하지 않습니다.")

        return {
            "message": "성공적으로 오버타임 정책 지점명별 조회에 성공하였습니다.",
            "data": result
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail="오버타임 정책 지점명별 조회에 에러가 발생하였습니다.")


# overtime 생성 [어드민만]
@router.post("/{branch_id}/overtime_policies")
async def time_create(overTimeCreate : OverTimeCreate, branch_id : int, token: Annotated[OverTimePolicies, Depends(validate_token)]):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="생성 권한이 없습니다.")
        
        
        create = OverTimePolicies(
            name = overTimeCreate.name,
            ot_30 = overTimeCreate.ot_30,
            ot_60 = overTimeCreate.ot_60,
            ot_90 = overTimeCreate.ot_90,
            ot_120 = overTimeCreate.ot_120
        )
        
        await overtime.add(create)
        await overtime.commit()
        await overtime.refresh(create)

        return {"message": "성공적으로 오버타임 정책 생성에 성공하였습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail="오버타임 정책 생성에 에러가 발생하였습니다.")


# overtime 수정 [어드민만]
@router.patch("/{branch_id}/overtime_policies/{id}")
async def time_edit(branch_id : int, id: int, overTimeUpdate : OverTimeUpdate, token: Annotated[OverTimePolicies, Depends(validate_token)]):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="생성 권한이 없습니다.")

        find_one_over_time = await overtime.execute(select(OverTimePolicies).where(OverTimePolicies.branch_id == branch_id, OverTimePolicies.id == id, OverTimePolicies.deleted_yn == "N"))
        result = find_one_over_time.scalar_one_or_none()

        if result == None:
            return JSONResponse(
                status_code=404, content="타임 데이터가 존재하지 않습니다."
            )

        result.name = overTimeUpdate.name
        result.ot_30 = overTimeUpdate.ot_30
        result.ot_60 = overTimeUpdate.ot_60
        result.ot_90 = overTimeUpdate.ot_90
        result.ot_120 = overTimeUpdate.ot_120

        await overtime.commit()

        return {"message": "성공적으로 오버타임 정책 수정에 성공하였습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(status_code= 500, detail="오버타임 정책 수정에 에러가 발생하였습니다.")

# overtime 데이터 삭제 [어드민만]
@router.delete("/{id}")
async def time_delete(id: int):
    try:
        find_over_time = overtime.query(OverTimePolicies).filter(OverTimePolicies.id == id).first()

        if find_over_time == None:
            return JSONResponse(
                status_code=404, content="타임 데이터가 존재하지 않습니다."
            )

        overtime.delete(find_over_time)
        overtime.commit()

        return {"message": "오버타임 데이터를 정상적으로 삭제하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)

# overtime 데이터 소프트 삭제 [어드민만]
@router.delete("/{branch_id}/overtime_policies/{id}")
async def time_soft_delete(id: int):
    try:
        find_over_time = overtime.query(OverTimePolicies).filter(OverTimePolicies.id == id).first()

        if find_over_time == None:
            return JSONResponse(
                status_code=404, content="타임 데이터가 존재하지 않습니다."
            )

        overtime.deleted_yn = "Y"

        return {"message": "오버타임 데이터를 정상적으로 삭제하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)



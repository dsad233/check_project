from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.future import select

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.models.policies.branchpolicies import OverTimePolicies

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
    

# overtime 파트별 검색 조회
@router.get("/{branch_id}/overtime_policies/{id}")
async def find_overtime_one (branch_id : int, branch_policy_id : int, id : int):
    try:
        overtime_one = await overtime.execute(select(OverTimePolicies).where(OverTimePolicies.branch_id == branch_id, OverTimePolicies.branch_policy_id == branch_policy_id, OverTimePolicies.id == id, OverTimePolicies.deleted_yn == "N"))
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

    

# overtime 지점애 따라 조회
@router.get("/{branch_id}/overtime_policies/{id}")
async def find_spot(spot: str):
    try:
        find_spot = await overtime.execute(
            select(OverTimePolicies).where(OverTimePolicies.overtime_id == id)
        )
        result = find_spot.scalar_one_or_none()

        if result == None:
            return JSONResponse(
                status_code=404, content="타임 데이터가 존재하지 않습니다."
            )

        return {
            "message": "지점별 오버타임 전체 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# overtime 상세 조회
@router.get("/{id}")
async def find_one(id: int):
    try:
        overtimeone = await overtime.execute(
            select(OverTimePolicies).where(OverTimePolicies.overtime_id == id)
        )
        result = overtimeone.scalar_one_or_none()

        if result == None:
            return JSONResponse(
                status_code=404, content="타임 데이터가 존재하지 않습니다."
            )

        return {
            "message": "오버타임 데이터 상세 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# overtime 생성
@router.post("")
async def time_create(token: Annotated[OverTimePolicies, Depends(validate_token)]):
    try:

        # overtimecreate = Overtime(
        #     proposer_id = token.id,
        #     application_note = schema.application_note
        # )

        # overtime.add(overtimecreate)
        # overtime.commit()
        # overtime.refresh(overtimecreate)

        return {"message": "오버타임 데이터 요청에 성공하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# overtime 수정 [어드민만]
@router.patch("/{id}")
async def time_edit(id: int, token: Annotated[OverTimePolicies, Depends(validate_token)]):
    try:

        find_over_time = overtime.query(OverTimePolicies).filter(OverTimePolicies.id == id).first()

        if find_over_time == None:
            return JSONResponse(
                status_code=404, content="타임 데이터가 존재하지 않습니다."
            )

        # find_over_time.manager_id = token.id
        # find_over_time.proposer_note = schema.proposer_note
        # find_over_time.processed_date = schema.processed_date
        # find_over_time.application_status = schema.application_status

        return {"message": "오버타임 데이터 업데이트에 성공하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# overtime 데이터 소프트 삭제 [어드민만]
@router.delete("/{id}")
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

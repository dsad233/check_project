from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select

from app.api.routes.branch_policies.schema.branch_schema import (
    BranchCreate,
    BranchUpdate,
)
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.models.models import Branches, Users
from app.models.policies.branchpolicies import BranchPolicies

router = APIRouter(dependencies=[Depends(validate_token)])
branch = async_session()


# 지점 정책 생성
@router.post("/{branch_id}/branch_policies")
async def create_policie(
    branch_id: int,
    branchCreate: BranchCreate,
    token=Annotated[Users, Depends(validate_token)],
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="생성 권한이 없습니다.")

        find_branch = await branch.execute(
            select(Branches).where(Branches.id == branch_id)
        )
        find_branch_result = find_branch.scalar_one_or_none()

        if find_branch_result == None:
            raise HTTPException(status_code=404, detail="지점이 존재하지 않습니다.")

        find_branch_policie = await branch.execute(
            select(BranchPolicies).where(
                BranchPolicies.branch_id == branch_id,
                BranchPolicies.name == branchCreate.name,
                BranchPolicies.policy_type == branchCreate.policy_type,
                BranchPolicies.deleted_yn == "N",
            )
        )
        find_branch_policie_result = find_branch_policie.scalar_one_or_none()

        if find_branch_policie_result != None:
            raise HTTPException(status_code=400, detail="이미 존재하는 정책명 입니다.")

        new_policie = BranchPolicies(
            branch_id=find_branch_result.id,
            name=branchCreate.name,
            policy_type=branchCreate.policy_type,
            effective_from=date,
        )

        await branch.add(new_policie)
        await branch.commit()
        await branch.refresh(new_policie)

        return {"message": "성공적으로 지점 정책 생성에 성공하였습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="서버 에러가 발생하였습니다.")


# 정책 전체 조회
@router.get("/branch_policies")
async def get_all():
    try:
        find_branch_policies_all = await branch.execute(
            select(BranchPolicies).where(BranchPolicies.deleted_yn == "N")
        )
        result = find_branch_policies_all.scalars().all()

        if len(result) == 0:
            raise HTTPException(
                status_code=404, detail="정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 정책 전체 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="정책 전체 조회에 에러가 발생하였습니다."
        )


# 지점 정책 전체 조회
@router.get("/{branch_id}/branch_policies")
async def get_all_policie(branch_id: int):
    try:
        find_branch_policie_all = await branch.execute(
            select(BranchPolicies)
            .where(
                BranchPolicies.branch_id == branch_id, BranchPolicies.deleted_yn == "N"
            )
            .offset(0)
            .limit(100)
        )
        result = find_branch_policie_all.scalars().all()

        if len(result) == 0:
            raise HTTPException(
                status_code=404, detail="지점 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 지점 정책 전체 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="지점 정책 전체 조회에 에러가 발생하였습니다."
        )


# 지점 정책 (제목) 조회
@router.get("/{branch_id}/branch_policies/{name}")
async def get_all_policie(branch_id: int, name: str):
    try:
        find_branch_policie_all = await branch.execute(
            select(BranchPolicies)
            .where(
                BranchPolicies.branch_id == branch_id,
                BranchPolicies.name.like(f"{name}%"),
                BranchPolicies.deleted_yn == "N",
            )
            .offset(0)
            .limit(100)
        )
        result = find_branch_policie_all.scalars().all()

        if len(result) == 0:
            raise HTTPException(
                status_code=404, detail="지점 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 지점 정책 전체 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="지점 정책 전체 조회에 에러가 발생하였습니다."
        )


# 지점 정책 상세 조회
@router.get("/{branch_id}/branch_policies/{id}")
async def get_one_policie(branch_id: int, id: int):
    try:
        find_branch_policie_one = await branch.execute(
            select(BranchPolicies).where(
                BranchPolicies.branch_id == branch_id,
                BranchPolicies.id == id,
                BranchPolicies.deleted_yn == "N",
            )
        )
        result = find_branch_policie_one.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="지점 정책 정보가 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 지점 정책 상세 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="지점 정책 상세 조회에 에러가 발생하였습니다."
        )


# 지점 정책 삭제 리스트만 전체 조회
@router.get("/{branch_id}/branch_policies/deletedlist")
async def get_delete_list(
    branch_id: int, token=Annotated[Users, Depends(validate_token)]
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="조호 권한이 없습니다.")

        find_branch_policie_deleted_all = await branch.execute(
            select(BranchPolicies)
            .where(
                BranchPolicies.branch_id == branch_id, BranchPolicies.deleted_yn == "Y"
            )
            .offset(0)
            .limit(100)
        )
        result = find_branch_policie_deleted_all.scalars().all()

        if len(result) == 0:
            raise HTTPException(
                status_code=404,
                detail="지점 정책들의 삭제 리스트 정보가 존재하지 않습니다.",
            )

        return {
            "message": "성공적으로 지점 정책 삭제 리스트 전체 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500,
            detail="지점 정책 삭제 리스트 전체 조회에 에러가 발생하였습니다.",
        )


# 지점 정책 삭제 리스트 상세 조회
@router.get("/{branch_id}/branch_policies/deletedlist/{id}")
async def get_one_delete_list(
    branch_id: int, id: int, token=Annotated[Users, Depends(validate_token)]
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="조회 권한이 없습니다.")

        find_branch_policie_deleted_one = await branch.execute(
            select(BranchPolicies).where(
                BranchPolicies.branch_id == branch_id,
                BranchPolicies.id == id,
                BranchPolicies.deleted_yn == "Y",
            )
        )
        result = find_branch_policie_deleted_one.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="지점 정책 정보가 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 지점 정책 삭제 리스트 상세 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500,
            detail="지점 정책 삭제 리스트 상세 조회에 에러가 발생하였습니다.",
        )


# 지점 정책 수정
@router.patch("/{branch_id}/branch_policies/{id}")
async def update_policie(
    branch_id: int,
    id: int,
    branchUpdate: BranchUpdate,
    token=Annotated[Users, Depends(validate_token)],
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

        find_branch_policie_one = await branch.execute(
            select(BranchPolicies).where(
                BranchPolicies.branch_id == branch_id,
                BranchPolicies.id == id,
                BranchPolicies.deleted_yn == "N",
            )
        )
        result = find_branch_policie_one.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="지점 정책 정보가 존재하지 않습니다."
            )

        result.name = branchUpdate.name
        result.policy_type = branchUpdate.policy_type
        result.effective_to = date

        await branch.commit()

        return {"message": "성공적으로 지점 정책 업데이트에 성공하였습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="지점 정책 업데이트에 에러가 발생하였습니다."
        )


# 지점 정책 마감일만 지정(수정)
@router.patch("/{branch_id}/branch_policies/{id}")
async def update_policie(
    branch_id: int, id: int, token=Annotated[Users, Depends(validate_token)]
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

        find_branch_policie_one = await branch.execute(
            select(BranchPolicies).where(
                BranchPolicies.branch_id == branch_id,
                BranchPolicies.id == id,
                BranchPolicies.deleted_yn == "N",
            )
        )
        result = find_branch_policie_one.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="지점 정책 정보가 존재하지 않습니다."
            )

        result.effective_to = date

        await branch.commit()

        return {"message": "성공적으로 지점 정책 업데이트에 성공하였습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="지점 정책 업데이트에 에러가 발생하였습니다."
        )


# 지점 정책 삭제
@router.delete("/{branch_id}/branch_policies/{id}")
async def delete_policie(
    branch_id: int, id: int, token=Annotated[Users, Depends(validate_token)]
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

        find_branch_policie_one = await branch.execute(
            select(BranchPolicies).where(
                BranchPolicies.branch_id == branch_id, BranchPolicies.id == id
            )
        )
        result = find_branch_policie_one.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="지점 정책 정보가 존재하지 않습니다."
            )

        await branch.delete(find_branch_policie_one)
        await branch.commit()

        return {"message": "성공적으로 지점 정책 업데이트에 성공하였습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="지점 정책 삭제에 에러가 발생하였습니다."
        )


# if(token.role != 'MSO 최고권한' | token.role != '최고관리자'):
#             raise HTTPException(status_code=403, detail='삭제 권한이 없습니다.')


# 지점 정책 소프트 삭제
@router.patch("/{branch_id}/branch_policies/softdelete/{id}")
async def softdelete_policie(
    branch_id: int, id: int, token=Annotated[Users, Depends(validate_token)]
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

        find_branch_policie_one = await branch.execute(
            select(BranchPolicies).where(
                BranchPolicies.branch_id == branch_id,
                BranchPolicies.id == id,
                BranchPolicies.deleted_yn == "N",
            )
        )
        result = find_branch_policie_one.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="지점 정책 정보가 존재하지 않습니다."
            )

        result.deleted_yn = "Y"

        await branch.commit()

        return {"message": "성공적으로 지점 정책 삭제에 성공하였습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="지점 정책 삭제에 에러가 발생하였습니다."
        )


# 지점 정책 복구
@router.patch("/{branch_id}/branch_policies/restore/{id}")
async def restore_policie(
    branch_id: int, id: int, token=Annotated[Users, Depends(validate_token)]
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

        find_branch_policie_deleted_one = await branch.execute(
            select(BranchPolicies).where(
                BranchPolicies.branch_id == branch_id,
                BranchPolicies.id == id,
                BranchPolicies.deleted_yn == "Y",
            )
        )
        result = find_branch_policie_deleted_one.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="지점 정책 정보가 존재하지 않습니다."
            )

        result.deleted_yn = "N"

        await branch.commit()

        return {"message": "성공적으로 지점 정책 복구에 성공하였습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="지점 정책 복구에 에러가 발생하였습니다."
        )

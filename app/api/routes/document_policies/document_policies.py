from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.models.branches.document_policies_model import DocumentPolicies
from app.models.users.users_model import Users

router = APIRouter(dependencies=[Depends(validate_token)])
document = async_session()


# 문서 정책 생성


# 문서 정책 전체 조회
@router.get("/{branch_id}/branch_policies/{branch_policy_id}/document_policies")
async def get_document(branch_id: int, branch_policy_id: int):
    try:
        find_document = await document.execute(
            select(DocumentPolicies)
            .where(
                DocumentPolicies.branch_id == branch_id,
                DocumentPolicies.branch_policy_id == branch_policy_id,
                DocumentPolicies.deleted_yn == "N",
            )
            .offset(0)
            .limit(100)
        )
        result = find_document.scalars().all()

        if len(result) == 0:
            raise HTTPException(
                status_code=404, detail="문서 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 문서 정책 전체 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="문서 정책 전체 조회에 에러가 발생하였습니다."
        )


# 문서 상세 조회
@router.get("/{branch_id}/branch_policies/{branch_policy_id}/document_policies/{id}")
async def get_one_document(branch_id: int, branch_policy_id: int, id: int):
    try:
        find_one_document = await document.execute(
            select(DocumentPolicies).where(
                DocumentPolicies.branch_id == branch_id,
                DocumentPolicies.branch_policy_id == branch_policy_id,
                DocumentPolicies.id == id,
                DocumentPolicies.deleted_yn == "N",
            )
        )
        result = find_one_document.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="문서 정책이 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 문서 정책 상세 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="문서 정책 상세 조회에 에러가 발생하였습니다."
        )


# 문서 정책 조회
@router.get("/{branch_id}/branch_policies/{branch_policy_id}/document_policies")
async def get_document(branch_id: int, branch_policy_id: int):
    try:
        find_document = await document.execute(
            select(DocumentPolicies)
            .where(
                DocumentPolicies.branch_id == branch_id,
                DocumentPolicies.branch_policy_id == branch_policy_id,
                DocumentPolicies.deleted_yn == "N",
            )
            .offset(0)
            .limit(100)
        )
        result = find_document.scalars().all()

        if len(result) == 0:
            raise HTTPException(
                status_code=404, detail="문서 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 문서 정책 전체 조회에 성공하였습니다.",
            "data": result,
        }
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="문서 정책 전체 조회에 에러가 발생하였습니다."
        )


# 문서 정책 수정
@router.patch("/{branch_id}/branch_policies/{branch_policy_id}/document_policies/{id}")
async def update_document(
    branch_id: int,
    branch_policy_id: int,
    id: int,
    token=Annotated[Users, Depends(validate_token)],
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        find_one_document = await document.execute(
            select(DocumentPolicies).where(
                DocumentPolicies.branch_id == branch_id,
                DocumentPolicies.branch_policy_id == branch_policy_id,
                DocumentPolicies.id == id,
                DocumentPolicies.deleted_yn == "N",
            )
        )
        result = find_one_document.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="문서 정책 정보가 존재하지 않습니다."
            )

    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="문서 정책 업데이트 에러가 발생하였습니다."
        )


# 문서 정책 삭제
@router.delete("/{branch_id}/branch_policies/{branch_policy_id}/document_policies/{id}")
async def delete_document(
    branch_id: int,
    branch_policy_id: int,
    id: int,
    token=Annotated[Users, Depends(validate_token)],
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        find_one_document = await document.execute(
            select(DocumentPolicies).where(
                DocumentPolicies.branch_id == branch_id,
                DocumentPolicies.branch_policy_id == branch_policy_id,
                DocumentPolicies.id == id,
                DocumentPolicies.deleted_yn == "N",
            )
        )
        result = find_one_document.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="문서 정책 정보가 존재하지 않습니다."
            )

        await document.delete(find_one_document)
        await document.commit()

        return {"message": "성공적으로 문서 정책 삭제에 성공하였습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="문서 정책 삭제 에러가 발생하였습니다."
        )


# 문서 정책 소프트 삭제
@router.patch(
    "/{branch_id}/branch_policies/{branch_policy_id}/document_policies/softdelete/{id}"
)
async def delete_document(
    branch_id: int,
    branch_policy_id: int,
    id: int,
    token=Annotated[Users, Depends(validate_token)],
):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        find_one_document = await document.execute(
            select(DocumentPolicies).where(
                DocumentPolicies.branch_id == branch_id,
                DocumentPolicies.branch_policy_id == branch_policy_id,
                DocumentPolicies.id == id,
                DocumentPolicies.deleted_yn == "N",
            )
        )
        result = find_one_document.scalar_one_or_none()

        if result == None:
            raise HTTPException(
                status_code=404, detail="문서 정책 정보가 존재하지 않습니다."
            )

        result.deleted_yn = "Y"

        await document.commit()

        return {"message": "성공적으로 문서 정책 삭제에 성공하였습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail="문서 정책 삭제 에러가 발생하였습니다."
        )


# 문서 정책 조회
# @router.get('/{branch_id}/branch_policies/{branch_policy_id}/document_policies')
# async def find_document(token=Annotated[Users, Depends(validate_token)]):
#     try:
#         if token.role != "MSO 최고권한" | token.role != "최고관리자":
#             raise HTTPException(status_code=403, detail="생성 권한이 없습니다.")

#         find_document = await document.execute(select(DocumentPolicies).where(DocumentPolicies.deleted_yn == "N"))
#         result = find_document.scalars().all()

#         if len(result) == 0:
#             raise HTTPException(
#                 status_code=404, detail="문서 정책들의 정보가 존재하지 않습니다."
#             )

#         return {
#             "message": "성공적으로 문서 정책 전체 조회에 성공하였습니다.",
#             "data": result,
#         }
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="문서 정책 전체 조회에 에러가 발생하였습니다.")

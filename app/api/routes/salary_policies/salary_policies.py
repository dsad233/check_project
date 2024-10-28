from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.cruds.branches.policies.salary_polices_crud import get_all_policies, update_policies
from app.models.branches.salary_polices_model import CombinedPoliciesResponse, CombinedPoliciesUpdate
from app.models.parts.salary_policies_model import SalaryPolicies
from app.models.users.users_model import Users
from app.middleware.tokenVerify import validate_token, get_current_user
from sqlalchemy.future import select
from app.core.database import async_session, get_db

router = APIRouter(dependencies=[Depends(validate_token)])
salay_policies = async_session()

# # 연봉 정책 생성
# @router.post('parts/{part_id}/salary_policies')
# async def create_salary_policies(branch_id : int, part_id : int):
#     try:
#         create = SalaryPolicies(
#             branch_id = branch_id,
#             part_id = part_id,
#         )
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="연봉 정책 생성에 실패하였습니다.")

# # 연봉 정책 전체 조회
# @router.get('parts/{part_id}/salary_policies')
# async def find_salary_policies(part_id : int, branch_id : int):
#     try:
#         find_all_salary_policies = await salay_policies.execute(select(SalaryPolicies).where(SalaryPolicies.branch_id == branch_id, SalaryPolicies.part_id == part_id, SalaryPolicies.deleted_yn == "N"))
#         result = find_all_salary_policies.scalars().all()
#         if(len(result) == 0):
#             raise HTTPException(status_code=404, detail="연봉 정책들이 존재하지 않습니다.")
        
#         return {"message": "성공적으로 연봉 정책 전체 조회에 성공하였습니다.", "data" : result}
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="연봉 정책 전체 조회에 실패하였습니다.")
    

# # 연봉 정책 상세 조회
# @router.get('parts/{part_id}/salary_policies/{id}')
# async def find_one_salary_policies(part_id : int, branch_id : int, id : int):
#     try:
#         find_one_salary_policies = await salay_policies.execute(select(SalaryPolicies).where(SalaryPolicies.branch_id == branch_id, SalaryPolicies.part_id == part_id, SalaryPolicies.id == id, SalaryPolicies.deleted_yn == "N"))
#         result = find_one_salary_policies.scalar_one_or_none()
        
#         if(result == None):
#             raise HTTPException(status_code=404, detail="연봉 정책이 존재하지 않습니다.")
        
#         return {"message": "성공적으로 연봉 정책 상세 조회에 성공하였습니다.", "data" : result}
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="연봉 정책 상세 조회에 실패하였습니다.")
    

# # 연봉 정책 수정 [어드민만]
# @router.patch('parts/{part_id}/salary_policies/{id}')
# async def update_salary_policies(part_id : int, branch_id : int, id : int, token:Annotated[Users, Depends(get_current_user)]):
#     try:
#         if token.role != "MSO 최고권한" or token.role != "최고관리자" or token.role != "통합관리자":
#             raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

#         find_one_salary_policies = await salay_policies.execute(select(SalaryPolicies).where(SalaryPolicies.branch_id == branch_id, SalaryPolicies.part_id == part_id, SalaryPolicies.id == id, SalaryPolicies.deleted_yn == "N"))
#         result = find_one_salary_policies.scalar_one_or_none()
        
#         if(result == None):
#             raise HTTPException(status_code=404, detail="연봉 정책이 존재하지 않습니다.")
        
#         find_one_salary_policies

#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="연봉 정책 수정에 실패하였습니다.")
    


# # 연봉 정책 삭제 [어드민만]
# @router.delete('parts/{part_id}/salary_policies/{id}')
# async def update_salary_policies(part_id : int, branch_id : int, id : int, token:Annotated[Users, Depends(get_current_user)]):
#     try:
#         if token.role != "MSO 최고권한" or token.role != "최고관리자" or token.role != "통합관리자":
#             raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

#         find_one_salary_policies = await salay_policies.execute(select(SalaryPolicies).where(SalaryPolicies.branch_id == branch_id, SalaryPolicies.part_id == part_id, SalaryPolicies.id == id, SalaryPolicies.deleted_yn == "N"))
#         result = find_one_salary_policies.scalar_one_or_none()
        
#         if(result == None):
#             raise HTTPException(status_code=404, detail="연봉 정책이 존재하지 않습니다.")
        
#         await salay_policies.delete(result)
#         await salay_policies.commit()

#         return {"message": "성공적으로 연봉 정책 삭제에 성공하였습니다."}
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="연봉 정책 삭제에 실패하였습니다.")



# # 연봉 정책 소프트 삭제 [어드민만]
# @router.patch('parts/{part_id}/salary_policies/softdelete/{id}')
# async def update_salary_policies(part_id : int, branch_id : int, id : int, token:Annotated[Users, Depends(get_current_user)]):
#     try:
#         if token.role != "MSO 최고권한" or token.role != "최고관리자" or token.role != "통합관리자":
#             raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

#         find_one_salary_policies = await salay_policies.execute(select(SalaryPolicies).where(SalaryPolicies.branch_id == branch_id, SalaryPolicies.part_id == part_id, SalaryPolicies.id == id, SalaryPolicies.deleted_yn == "N"))
#         result = find_one_salary_policies.scalar_one_or_none()
        
#         if(result == None):
#             raise HTTPException(status_code=404, detail="연봉 정책이 존재하지 않습니다.")
        
#         result.deleted_yn = "Y"

#         await salay_policies.commit()

#         return {"message": "성공적으로 연봉 정책 삭제에 성공하였습니다."}
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="연봉 정책 삭제에 실패하였습니다.")


# # 연봉 정책 복구 [어드민만]
# @router.patch('parts/{part_id}/salary_policies/restore/{id}')
# async def update_salary_policies(part_id : int, branch_id : int, id : int, token:Annotated[Users, Depends(get_current_user)]):
#     try:
#         if token.role != "MSO 최고권한" | token.role != "최고관리자" or token.role != "통합관리자":
#             raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

#         find_one_salary_policies = await salay_policies.execute(select(SalaryPolicies).where(SalaryPolicies.branch_id == branch_id, SalaryPolicies.part_id == part_id, SalaryPolicies.id == id, SalaryPolicies.deleted_yn == "N"))
#         result = find_one_salary_policies.scalar_one_or_none()
        
#         if(result == None):
#             raise HTTPException(status_code=404, detail="연봉 정책이 존재하지 않습니다.")
        
#         result.deleted_yn = "N"

#         await salay_policies.commit()

#         return {"message": "성공적으로 연봉 정책 삭제에 성공하였습니다."}
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="연봉 정책 삭제에 실패하였습니다.")
    

@router.get("/combined", response_model=CombinedPoliciesResponse)
async def read_all_policies(
    branch_id: int,
    db: Session = Depends(get_db)
):
    """
    임금 명세서 설정 조회
    """
    policies = await get_all_policies(db, branch_id)
    if not any(policies.values()):
        raise HTTPException(status_code=404, detail="정책을 찾을 수 없습니다")
    return policies

@router.patch("/combined", response_model=CombinedPoliciesResponse)
async def update_all_policies(
    update_data: CombinedPoliciesUpdate,  # 기본값이 없는 매개변수를 앞으로
    branch_id: int,
    current_user: Annotated[Users, Depends(get_current_user)],
    db: Session = Depends(get_db),  # 기본값이 있는 매개변수를 뒤로
):
    """
    임금 명세서 설정 조회
    """
    # 권한 체크
    if current_user.role not in ["MSO 최고권한", "최고관리자", "통합관리자"]:
        raise HTTPException(status_code=403, detail="정책 수정 권한이 없습니다")
    
    try:
        updated_policies = await update_policies(db, branch_id, update_data)
        return updated_policies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정책 수정 중 오류가 발생했습니다: {str(e)}")

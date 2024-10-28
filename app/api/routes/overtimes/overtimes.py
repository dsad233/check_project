from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update

from app.core.database import async_session
from app.middleware.tokenVerify import get_current_user, get_current_user_id, validate_token
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.overtimes_model import OvertimeSelect, OvertimeCreate, Overtimes, OvertimeUpdate, OverTime_History
from app.models.branches.overtime_policies_model import OverTimePolicies
from app.models.users.users_model import Users
from sqlalchemy.orm import load_only
from app.enums.users import OverTimeHours

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


# 오버타임 초과 근무 생성(신청)
@router.post("", summary="오버타임 초과 근무 생성")
async def create_overtime(overtime: OvertimeCreate, current_user_id: int = Depends(get_current_user_id)):
    try:        
        new_overtime = Overtimes(
            applicant_id=current_user_id,
            application_date = overtime.application_date,
            overtime_hours=overtime.overtime_hours,
            application_memo=overtime.application_memo,
        )

        db.add(new_overtime)
        await db.commit()
        await db.refresh(new_overtime)

        
        return {
            "message": "초과 근무 기록이 성공적으로 생성되었습니다.",
            "data": new_overtime,
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error : {str(err)}")


# 오버타임 관리자 메모 상세 조회
@router.get('/manager/{id}', summary="오버타임 관리자 메모 상세 조회")
async def get_manager(id : int):
    try:
        find_manager_data = await db.execute(select(Overtimes).options(load_only(Overtimes.manager_memo)).where(Overtimes.id == id, Overtimes.deleted_yn == "N"))

        return {
            "message": "관리자 메모 조회가 완료 되었습니다.",
            "data": find_manager_data,
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error : {str(err)}")
    

# 오버타임 초과 근무 승인
@router.patch("/approve/{overtime_id}", summary="오버타임 승인")
async def approve_overtime(overtime_id: int, overtime_select: OvertimeSelect, current_user: Users = Depends(get_current_user)):
    try:
        stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N") & (Overtimes.status == "pending"))
        result = await db.execute(stmt)
        overtime = result.scalar_one_or_none()
        
        if overtime is None:
            raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")

        if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자", "통합관리자"]:
            raise HTTPException(status_code=403, detail="관리자만 승인할 수 있습니다.")
        
        overtime.status = "approved"
        overtime.manager_id = current_user.id
        overtime.manager_name = current_user.name
        overtime.processed_date = datetime.now(UTC).date()
        overtime.is_approved = "Y"
        overtime.manager_memo = overtime_select.manager_memo

        # new_overtime_history = OverTime_History(
        #     user_id = overtime.applicant_id,
        # )
        
        # db.add(new_overtime_history)
        # await db.commit()
        # await db.refresh(new_overtime_history)

        # # 해당 파트에 대한 의사 여부 확인
        # find_part = await db.execute(select(Parts).join(Users, Parts.id == Users.part_id).where(Users.id == overtime.applicant_id, Parts.is_doctor == True, Parts.deleted_yn == "N", Users.deleted_yn == "N"))
        # result_part = find_part.first()

        # if not result_part:
        #         raise HTTPException(status_code=404, detail="사용자 또는 파트 정보를 찾을 수 없습니다.")

        # find_overtime_policies = await db.scalars(select(OverTimePolicies).join(Branches, Branches.id == OverTimePolicies.branch_id).options(load_only(OverTimePolicies.doctor_ot_30, OverTimePolicies.doctor_ot_60, OverTimePolicies.doctor_ot_90, OverTimePolicies.common_ot_30, OverTimePolicies.common_ot_60, OverTimePolicies.common_ot_90)).where(Branches.id == OverTimePolicies.branch_id, OverTimePolicies.branch_id == Users.branch_id, Branches.deleted_yn == "N", OverTimePolicies.deleted_yn == "N"))
        # result_overtime_policies = find_overtime_policies.first()

        # if not result_overtime_policies:
        #         raise HTTPException(status_code=404, detail="오버타임 정책을 찾을 수 없습니다.")

        # # 기존 데이터의 테이블이 쌓이는 문제가 발생
        # if(overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.THIRTY_MINUTES):
        #     new_overtime_history.ot_30_total += 1
        #     new_overtime_history.ot_30_money += result_overtime_policies.doctor_ot_30 if result_part.is_doctor else result_overtime_policies.common_ot_30
        # elif(overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.SIXTY_MINUTES):
        #     new_overtime_history.ot_60_total += 1
        #     new_overtime_history.ot_60_money += result_overtime_policies.doctor_ot_60 if result_part.is_doctor else result_overtime_policies.common_ot_60
        # elif(overtime.overtime_hours != None and overtime.overtime_hours == OverTimeHours.NINETY_MINUTES):
        #     new_overtime_history.ot_90_total += 1
        #     new_overtime_history.ot_90_money += result_overtime_policies.doctor_ot_90 if result_part.is_doctor else result_overtime_policies.common_ot_90

        # 테스트 중인 코드
        new_overtime_history = OverTime_History(
            user_id=overtime.applicant_id,
            ot_30_total=0,
            ot_60_total=0,
            ot_90_total=0,
            ot_30_money=0,
            ot_60_money=0,
            ot_90_money=0
        )
        
        db.add(new_overtime_history)
        await db.commit()
        await db.refresh(new_overtime_history)

        # 해당 파트에 대한 의사 여부 확인
        find_part = await db.execute(
            select(Parts)
            .join(Users, Parts.id == Users.part_id)
            .where(
                Users.id == overtime.applicant_id,
                Parts.deleted_yn == "N",
                Users.deleted_yn == "N"
            )
        )
        result_part = find_part.first()

        if not result_part:
            raise HTTPException(status_code=404, detail="사용자 또는 파트 정보를 찾을 수 없습니다.")

        # 오버타임 정책 조회
        find_overtime_policies = await db.execute(
            select(OverTimePolicies)
            .join(Branches, OverTimePolicies.branch_id == Branches.id)
            .join(Users, Users.branch_id == Branches.id)
            .where(
                Users.id == overtime.applicant_id,
                Branches.deleted_yn == "N",
                OverTimePolicies.deleted_yn == "N"
            )
        )
        result_overtime_policies = find_overtime_policies.first()

        if not result_overtime_policies:
            raise HTTPException(status_code=404, detail="오버타임 정책을 찾을 수 없습니다.")

        # 오버타임 시간에 따른 금액 계산
        if overtime.overtime_hours == OverTimeHours.THIRTY_MINUTES:
            new_overtime_history.ot_30_total = 1
            new_overtime_history.ot_30_money = result_overtime_policies[0].doctor_ot_30 if result_part[0].is_doctor else result_overtime_policies[0].common_ot_30
        elif overtime.overtime_hours == OverTimeHours.SIXTY_MINUTES:
            new_overtime_history.ot_60_total = 1
            new_overtime_history.ot_60_money = result_overtime_policies[0].doctor_ot_60 if result_part[0].is_doctor else result_overtime_policies[0].common_ot_60
        elif overtime.overtime_hours == OverTimeHours.NINETY_MINUTES:
            new_overtime_history.ot_90_total = 1
            new_overtime_history.ot_90_money = result_overtime_policies[0].doctor_ot_90 if result_part[0].is_doctor else result_overtime_policies[0].common_ot_90

        await db.commit()
        
        return {
            "message": "초과 근무 기록이 승인되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error {str(err)}")


# 오버타임 초과 근무 거절
@router.patch("/reject/{overtime_id}", summary="오버타임 반려")
async def reject_overtime(overtime_id: int, overtime_select: OvertimeSelect, current_user: Users = Depends(get_current_user)):
    try:
        stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N"))
        result = await db.execute(stmt)
        overtime = result.scalar_one_or_none()
        
        if overtime is None:
            raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")

        if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자", "통합관리자"]:
            raise HTTPException(status_code=403, detail="관리자만 승인할 수 있습니다.")
        
        overtime.status = "rejected"
        overtime.manager_id = current_user.id
        overtime.manager_name = current_user.name
        overtime.processed_date = datetime.now(UTC).date()
        overtime.is_approved = "N"
        overtime.manager_memo = overtime_select.manager_memo
        await db.commit()
        
        return {
            "message": "초과 근무 기록이 거절되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error {str(err)}")

# 초과 근무 목록 조회
@router.get("")
async def get_overtimes(current_user: Users = Depends(get_current_user), skip: int = 0, limit: int = 100, name: str = None, phone_number: str = None, branch: str = None, part: str = None, status: str = None):
    try:
        stmt = None
        base_query = (
            select(Overtimes)
            .where(Overtimes.deleted_yn == "N")
        )
        
        # 사원인 경우 자신의 기록만 조회
        if current_user.role == "사원":
            base_query = base_query.where(Overtimes.applicant_id == current_user.id)

        # Users 테이블과 JOIN (검색 조건이 있는 경우)
        if name or phone_number or branch or part:
            base_query = base_query.join(Users, Overtimes.applicant_id == Users.id)

        # 이름 검색 조건
        if name:
            base_query = base_query.where(Users.name.like(f"%{name}%"))
        # 전화번호 검색 조건
        elif phone_number:
            base_query = base_query.where(Users.phone_number.like(f"%{phone_number}%"))
        # 지점 검색 조건
        if branch:
            base_query = base_query.join(Branches, Users.branch_id == Branches.id)\
                .where(Branches.name.like(f"%{branch}%"))
        # 파트 검색 조건
        if part:
            base_query = base_query.join(Parts, Users.part_id == Parts.id)\
                .where(Parts.name.like(f"%{part}%"))
        # 상태 검색 조건
        if status:
            base_query = base_query.where(Overtimes.status.like(f"%{status}%"))

        # 정렬, 페이징 적용
        stmt = base_query.order_by(Overtimes.application_date.desc())\
            .offset(skip)\
            .limit(limit)

        result = await db.execute(stmt)
        overtimes = result.scalars().all()

        count_query = base_query.with_only_columns(func.count())
        total_count = await db.execute(count_query)
        total_count = total_count.scalar_one()

        return {
            "message": "초과 근무 기록을 정상적으로 조회하였습니다.",
            "data": overtimes,
            "total": total_count,
            "skip": skip,
            "limit": limit,
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error {str(err)}")


# # 초과 근무 수정
# @router.patch("/{overtime_id}")
# async def update_overtime(overtime_id: int, overtime_update: OvertimeUpdate, current_user: Users = Depends(get_current_user)):
#     try:
#         stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N"))
#         result = await db.execute(stmt)
#         overtime = result.scalar_one_or_none()

#         if overtime is None:
#             raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")

#         if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자", "통합관리자"] or current_user.id != overtime.applicant_id:
#             raise HTTPException(status_code=403, detail="관리자 또는 초과 근무 신청자만 수정할 수 있습니다.")

#         if overtime.status != "pending":
#             raise HTTPException(status_code=400, detail="승인 또는 거절된 초과 근무는 수정할 수 없습니다.")

#         update_data = {}

#         # 관리자인 경우
#         if current_user.role in ["MSO 최고권한", "최고관리자", "관리자", "통합관리자"]:
#             if overtime_update.overtime_hours is not None:
#                 update_data["overtime_hours"] = overtime_update.overtime_hours
#             if overtime_update.application_memo is not None:
#                 update_data["application_memo"] = overtime_update.application_memo
#             if overtime_update.manager_memo is not None:
#                 update_data["manager_memo"] = overtime_update.manager_memo

#         # 신청자인 경우
#         elif current_user.id == overtime.applicant_id:
#             if overtime_update.application_memo is not None:
#                 update_data["application_memo"] = overtime_update.application_memo
        
#         else:
#             raise HTTPException(status_code=403, detail="초과 근무 기록을 수정할 권한이 없습니다.")

#         if not update_data:
#             raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")

#         update_stmt = update(Overtimes).where(Overtimes.id == overtime_id).values(**update_data)
#         await db.execute(update_stmt)
#         await db.commit()
        
#         return {
#             "message": "초과 근무 기록이 수정되었습니다.",
#         }
#     except HTTPException as http_err:
#         await db.rollback() 
#         raise http_err
#     except Exception as err:
#         await db.rollback()
#         print("에러가 발생하였습니다.")
#         print(err)
#         raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# # 초과 근무 삭제 (신청 취소)
# @router.delete("/{overtime_id}")
# async def delete_overtime(overtime_id: int, current_user: Users = Depends(get_current_user)):
#     try:
#         stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N") & (Overtimes.status == "pending"))
#         result = await db.execute(stmt)
#         overtime = result.scalar_one_or_none()

#         if overtime is None:
#             raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")
        
#         if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자", "통합관리자"] or current_user.id != overtime.applicant_id:
#             raise HTTPException(status_code=403, detail="관리자 또는 초과 근무 신청자만 삭제할 수 있습니다.")

#         if overtime.status != "pending":
#             raise HTTPException(status_code=400, detail="승인 또는 거절된 초과 근무는 삭제할 수 없습니다.")

#         update_stmt = update(Overtimes).where(Overtimes.id == overtime_id).values(deleted_yn="Y")
#         await db.execute(update_stmt)
#         await db.commit()
        
#         return {
#             "message": "초과 근무 기록이 삭제되었습니다.",
#         }
#     except HTTPException as http_err:
#         await db.rollback()
#         raise http_err
#     except Exception as err:
#         await db.rollback()
#         print("에러가 발생하였습니다.")
#         print(err)
#         raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
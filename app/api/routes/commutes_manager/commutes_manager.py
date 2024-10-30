import re
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from typing import Annotated, Any, Dict, List, Optional
from app.common.dto.pagination_dto import PaginationDto
from app.core.database import async_session, get_db
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.branches.leave_categories_model import LeaveCategory
from app.models.branches.rest_days_model import RestDays
from app.models.closed_days.closed_days_model import ClosedDays
from app.models.users.leave_histories_model import LeaveHistories
from app.models.users.users_model import Users
from app.models.parts.parts_model import Parts
from app.models.commutes.commutes_model import Commutes
from app.models.branches.branches_model import Branches
from app.models.branches.work_policies_model import WorkPolicies
from sqlalchemy.future import select
from sqlalchemy.orm import load_only, selectinload, subqueryload
from sqlalchemy import and_, distinct, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from calendar import monthrange
from fastapi.responses import StreamingResponse
import pandas as pd
import io


router = APIRouter(dependencies=[Depends(validate_token)])


""" 출퇴근 관리 결근 상태 조회 """


async def get_absence_status(session, user, check_date: date) -> str:
    try:
        if user.resignation_date and check_date > user.resignation_date:
            return "퇴사"
        if check_date < user.hire_date:
            return "미입사"
        if user.role == Role.ON_LEAVE:
            return "휴직"
        
        # 승인된 휴가 체크
        leave_history = await session.scalar(
            select(LeaveHistories).where(
                and_(
                    LeaveHistories.user_id == user.id,
                    LeaveHistories.application_date == check_date,
                    LeaveHistories.status == "승인",
                    LeaveHistories.deleted_yn == "N"
                )
            ).options(selectinload(LeaveHistories.leave_category))
        )

        if leave_history:
            return leave_history.leave_category.name

        # 휴무일 체크
        rest_day = await session.scalar(
            select(RestDays).where(
                and_(
                    RestDays.branch_id == user.branch_id,
                    RestDays.date == check_date,
                    RestDays.deleted_yn == "N",
                )
            )
        )

        if rest_day:
            return f"휴무({rest_day.rest_type})"

        # 휴점일 체크
        closed_day_query = select(ClosedDays).where(
            and_(
                ClosedDays.branch_id == user.branch_id,
                ClosedDays.closed_day_date == check_date,
                ClosedDays.deleted_yn == "N",
            )
        )
        closed_day = await session.scalar(closed_day_query)

        if closed_day:
            return "휴점"

        return "결근"
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"출퇴근 기록 조회 실패: {str(e)}")


""" 출퇴근 관리 한 달 기록 생성 """


async def create_daily_records(
    session, year: int, month: int, user, work_policy
) -> List[Dict]:
    today = date.today()
    _, last_day = monthrange(year, month)

    if year == today.year and month == today.month:
        last_day = today.day

    daily_records = []
    for day in range(1, last_day + 1):
        check_date = date(year, month, day)
        # 일요일 체크 (weekday()가 6이면 일요일)
        if check_date.weekday() == 6:
            daily_record = {
                "date": check_date.strftime("%Y-%m-%d"),
                "status": "일요일 정기휴무",
            }
        else:
            status = await get_absence_status(session, user, check_date)
            daily_record = {
                "date": check_date.strftime("%Y-%m-%d"),
                "status": status,
            }

        daily_records.append(daily_record)

    return daily_records


""" 출퇴근 관리 기록 조회 """


@router.get("/commutes-manager", response_model=Dict[str, Any])
@available_higher_than(Role.ADMIN)
async def get_commutes_manager(
    request: Request,
    db: Annotated[AsyncSession,Depends(get_db)],
    branch: Optional[int] = Query(None, description="지점 ID"),
    part: Optional[int] = Query(None, description="파트 ID"),
    name: Optional[str] = Query(None, description="사용자 이름"),
    phone_number: Optional[str] = Query(None, description="전화번호"),
    year_month: Optional[str] = Query(None, description="조회 년월 (YYYY-MM 형식)"),
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
):
    if part and not branch:
        raise HTTPException(status_code=400, detail="지점 정보가 필요합니다.")

    try:
        async with db as session:
            today = datetime.now()
            if year_month:
                if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", year_month):
                    raise HTTPException(
                        status_code=400, detail="올바른 년월 형식이 아닙니다. (YYYY-MM)"
                    )
                date_obj = datetime.strptime(year_month, "%Y-%m")
                year = date_obj.year
                month = date_obj.month
            else:
                year = today.year
                month = today.month

            start_date = date(year, month, 1)
            end_date = min(date(year, month, monthrange(year, month)[1]), date.today())

            # 사용자 및 출퇴근 기록 조회
            query = (
                select(Users)
                .options(
                    # 필요한 컬럼만 로드
                    load_only(
                        Users.id,
                        Users.name,
                        Users.gender,
                        Users.branch_id,
                        Users.part_id,
                        Users.hire_date,
                        Users.resignation_date,
                        Users.role,
                    ),
                    # 관련 테이블에서도 필요한 컬럼만 로드
                    subqueryload(Users.branch).load_only(Branches.id, Branches.name),
                    subqueryload(Users.part).load_only(Parts.id, Parts.name),
                    # 해당 기간의 출퇴근 기록만 로드
                    subqueryload(
                        Users.commutes.and_(
                            Commutes.clock_in >= start_date,
                            Commutes.clock_in <= end_date,
                            Commutes.deleted_yn == "N",
                        )
                    ),
                )
                .join(Branches, Users.branch_id == Branches.id)
                .join(
                    WorkPolicies,
                    and_(
                        WorkPolicies.branch_id == Branches.id,
                        WorkPolicies.deleted_yn == "N",
                    ),
                )
                .where(Users.deleted_yn == "N")
            )

            if branch:
                query = query.where(Users.branch_id == branch)
            if part:
                query = query.where(Users.part_id == part)
            if name:
                query = query.where(Users.name == name)
            if phone_number:
                query = query.where(Users.phone_number == phone_number)

            total_count = await session.scalar(
                select(func.count()).select_from(query.subquery())
            )

            # 페이지네이션 적용
            pagination = PaginationDto(
                total_record=total_count,
                record_size=size
            )
            users = query.offset((page - 1) * pagination.record_size).limit(pagination.record_size)
            users = await session.execute(users)
            users = users.scalars().unique().all()

            formatted_data = []
            for user in users:
                # 근무 정책 조회
                work_policy = await session.scalar(
                    select(WorkPolicies).where(
                        and_(
                            WorkPolicies.branch_id == user.branch_id,
                            WorkPolicies.deleted_yn == "N",
                        )
                    )
                )

                daily_records = await create_daily_records(
                    session, year, month, user, work_policy
                )

                # 출퇴근 기록 매핑
                for commute in user.commutes:
                    if (
                        commute.deleted_yn == "N"
                        and start_date <= commute.clock_in.date() <= end_date
                    ):
                        day_idx = commute.clock_in.day - 1

                        # 지각, 초과근무 체크
                        if work_policy:
                            is_holiday = "휴무" in daily_records[day_idx]["status"]
                            
                            if commute.clock_in:
                                # 휴무일인 경우 토요일 시간으로 체크, 아닌 경우 평일 시간으로 체크
                                policy_start_time = (
                                    work_policy.saturday_start_time 
                                    if is_holiday 
                                    else work_policy.weekday_start_time
                                )
                                
                                if policy_start_time:
                                    policy_start = datetime.combine(
                                        commute.clock_in.date(),
                                        policy_start_time,
                                    )
                                    late = (commute.clock_in - policy_start).total_seconds() > 0

                            if commute.clock_out:
                                # 휴무일인 경우 토요일 시간으로 체크, 아닌 경우 평일 시간으로 체크
                                policy_end_time = (
                                    work_policy.saturday_end_time 
                                    if is_holiday 
                                    else work_policy.weekday_end_time
                                )
                                
                                if policy_end_time:
                                    policy_end = datetime.combine(
                                        commute.clock_in.date(),
                                        policy_end_time,
                                    )
                                    overtime = (commute.clock_out - policy_end).total_seconds() > 0

                        # 휴무일이 아닌 경우에만 상태를 "출근"으로 변경
                        if "휴무" not in daily_records[day_idx]["status"]:
                            daily_records[day_idx].update(
                                {
                                    "clock_in": commute.clock_in.strftime("%H:%M:%S"),
                                    "clock_out": (
                                        commute.clock_out.strftime("%H:%M:%S")
                                        if commute.clock_out
                                        else None
                                    ),
                                    "work_hours": commute.work_hours,
                                    "status": "출근",
                                    "late": late,
                                    "overtime": overtime,
                                }
                            )
                        else:
                            # 휴무일인 경우 상태는 유지하고 출퇴근 정보만 추가
                            daily_records[day_idx].update(
                                {
                                    "clock_in": commute.clock_in.strftime("%H:%M:%S"),
                                    "clock_out": (
                                        commute.clock_out.strftime("%H:%M:%S")
                                        if commute.clock_out
                                        else None
                                    ),
                                    "work_hours": commute.work_hours,
                                    "late": late,
                                    "overtime": overtime,
                                }
                            )

                user_data = {
                    "user_id": user.id,
                    "user_name": user.name,
                    "user_gender": user.gender,
                    "branch_id": user.branch_id,
                    "branch_name": user.branch.name,
                    "part_name": user.part.name,
                    "weekly_work_days": (
                        work_policy.weekly_work_days if work_policy else None
                    ),
                    "commute_records": daily_records,
                }
                formatted_data.append(user_data)

            return {
                "message": "출퇴근 기록 조회 성공",
                "data": formatted_data,
                "pagination": {
                    "total": total_count,
                    "page": page,
                    "size": size,
                },
            }

    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"출퇴근 기록 조회 실패: {str(e)}")


""" 유틸 """
# FE 에서 처리


# 출 퇴근 관리 기록 전체 조회 엑셀 다운로드
# @router.get("/commutes-manager/excel")
# async def get_all_commutes_manager_excel(
#     token: Annotated[Users, Depends(get_current_user)]
# ):
#     try:

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(
#             select(Commutes)
#             .where(Commutes.deleted_yn == "N")
#             .order_by(Commutes.clock_in.asc())
#         )
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(
#             select(ClosedDays)
#             .where(ClosedDays.deleted_yn == "N")
#             .options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date))
#         )
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(
#             select(Users, Branches, Parts)
#             .join(Branches, Branches.id == Users.branch_id)
#             .join(Parts, Parts.id == Users.part_id)
#             .options(
#                 load_only(Users.id, Users.name, Users.gender),
#                 load_only(Branches.name),
#                 load_only(Parts.name),
#             )
#             .distinct(Users.id)
#             .where(
#                 Users.deleted_yn == "N",
#                 Branches.deleted_yn == "N",
#                 Parts.deleted_yn == "N",
#             )
#             .order_by(Users.name.asc())
#         )
#         result = find_data.fetchall()

#         # 데이터를 pandas DataFrame으로 변환
#         df_users = pd.DataFrame(
#             [
#                 {
#                     "사용자 ID": row.Users.id,
#                     "이름": row.Users.name,
#                     "성별": row.Users.gender,
#                     "부서": row.Parts.name,
#                     "지점": row.Branches.name,
#                 }
#                 for row in result
#             ]
#         )

#         df_commutes = pd.DataFrame([
#             {
#                 "사용자 ID": commute.request_user_id,
#                 "출근 시간": commute.clock_in,
#                 "퇴근 시간": commute.clock_out,
#                 "근무 시간": commute.work_hours,
#             }
#             for commute in result_work_data
#         ])

#         df_closed_days = pd.DataFrame([
#             {
#                 "사용자 ID": closed_day.request_user_id,
#                 "휴가 날짜": closed_day.closed_day_date,
#             }
#             for closed_day in result_closed_day
#         ])

#         # Excel 파일 생성
#         output = io.BytesIO()
#         with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#             df_users.to_excel(writer, sheet_name="사용자 정보", index=False)
#             df_commutes.to_excel(writer, sheet_name="출퇴근 기록", index=False)
#             df_closed_days.to_excel(writer, sheet_name="휴가 기록", index=False)
#         output.seek(0)

#         # 스트리밍 응답으로 Excel 파일 반환
#         return StreamingResponse(
#             output,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={
#                 "Content-Disposition": f"attachment; filename=commutes_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
#             },
#         )

#     except Exception as err:
#         print(err)
#         raise HTTPException(
#             status_code=500, detail="출퇴근 데이터 엑셀 파일 생성에 실패하였습니다."
#         )


# # 출 퇴근 관리 기록 date로 전체 조회 엑셀 다운로드
# @router.get("/commutes-manager/date/excel")
# async def get_all_date_commutes_manager_excel(
#     date: str, token: Annotated[Users, Depends(get_current_user)]
# ):
#     try:
#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)

#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(
#             select(Commutes)
#             .join(Users)
#             .where(
#                 Commutes.deleted_yn == "N",
#                 Commutes.clock_in >= date_start_day,
#                 Commutes.clock_in <= date_end_day,
#             )
#             .order_by(Commutes.clock_in.asc())
#         )
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(
#             select(ClosedDays)
#             .join(Users)
#             .where(
#                 ClosedDays.deleted_yn == "N",
#                 ClosedDays.closed_day_date >= date_start_day,
#                 ClosedDays.closed_day_date <= date_end_day,
#             )
#             .options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date))
#         )
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(
#             select(Users, Branches, Parts)
#             .join(Branches, Branches.id == Users.branch_id)
#             .join(Parts, Parts.id == Users.part_id)
#             .options(
#                 load_only(Users.id, Users.name, Users.gender),
#                 load_only(Branches.name),
#                 load_only(Parts.name),
#             )
#             .distinct(Users.id)
#             .where(
#                 Users.deleted_yn == "N",
#                 Branches.deleted_yn == "N",
#                 Parts.deleted_yn == "N",
#             )
#             .order_by(Users.name.asc())
#         )
#         result = find_data.fetchall()

#         # 데이터를 pandas DataFrame으로 변환
#         df_users = pd.DataFrame(
#             [
#                 {
#                     "사용자 ID": row.Users.id,
#                     "이름": row.Users.name,
#                     "성별": row.Users.gender,
#                     "부서": row.Parts.name,
#                     "지점": row.Branches.name,
#                 }
#                 for row in result
#             ]
#         )

#         df_commutes = pd.DataFrame([
#             {
#                 "사용자 ID": commute.request_user_id,
#                 "출근 시간": commute.clock_in,
#                 "퇴근 시간": commute.clock_out,
#                 "근무 시간": commute.work_hours,
#             }
#             for commute in result_work_data
#         ])

#         df_closed_days = pd.DataFrame([
#             {
#                 "사용자 ID": closed_day.request_user_id,
#                 "휴가 날짜": closed_day.closed_day_date,
#             }
#             for closed_day in result_closed_day
#         ])

#         # Excel 파일 생성
#         output = io.BytesIO()
#         with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#             df_users.to_excel(writer, sheet_name="사용자 정보", index=False)
#             df_commutes.to_excel(writer, sheet_name="출퇴근 기록", index=False)
#             df_closed_days.to_excel(writer, sheet_name="휴가 기록", index=False)
#         output.seek(0)

#         # 스트리밍 응답으로 Excel 파일 반환
#         return StreamingResponse(
#             output,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={
#                 "Content-Disposition": f"attachment; filename=all_commutes_report_{date}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
#             },
#         )

#     except Exception as err:
#         print(err)
#         raise HTTPException(
#             status_code=500,
#             detail="날짜별 전체 출퇴근, 휴가 데이터 및 사용자 정보 엑셀 파일 생성에 실패하였습니다.",
#         )


# # 출 퇴근 관리 기록 지점별 전체 조회 엑셀 다운로드
# @router.get("/{branch_id}/commutes-manager/excel")
# async def get_branch_all_commutes_manager_excel(
#     branch_id: int, date: str, token: Annotated[Users, Depends(get_current_user)]
# ):
#     try:
#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)

#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(
#             select(Commutes)
#             .where(
#                 Users.branch_id == branch_id,
#                 Commutes.deleted_yn == "N",
#                 Commutes.clock_in >= date_start_day,
#                 Commutes.clock_in <= date_end_day,
#             )
#             .order_by(Commutes.clock_in.asc())
#         )
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(
#             select(ClosedDays)
#             .where(ClosedDays.deleted_yn == "N")
#             .options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date))
#         )
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(
#             select(Users, Branches, Parts)
#             .join(Branches, Branches.id == Users.branch_id)
#             .join(Parts, Parts.id == Users.part_id)
#             .options(
#                 load_only(Users.id, Users.name, Users.gender),
#                 load_only(Branches.name),
#                 load_only(Parts.name),
#             )
#             .distinct(Users.id)
#             .where(
#                 Users.deleted_yn == "N",
#                 Branches.id == branch_id,
#                 Branches.deleted_yn == "N",
#                 Parts.deleted_yn == "N",
#                 Commutes.clock_in >= date_start_day,
#                 Commutes.clock_in <= date_end_day,
#                 Commutes.deleted_yn == "N",
#             )
#             .order_by(Users.name.asc())
#         )
#         result = find_data.fetchall()

#         # 데이터를 pandas DataFrame으로 변환
#         df_users = pd.DataFrame(
#             [
#                 {
#                     "사용자 ID": row.Users.id,
#                     "이름": row.Users.name,
#                     "성별": row.Users.gender,
#                     "부서": row.Parts.name,
#                     "지점": row.Branches.name,
#                 }
#                 for row in result
#             ]
#         )

#         df_commutes = pd.DataFrame([
#             {
#                 "사용자 ID": commute.request_user_id,
#                 "출근 시간": commute.clock_in,
#                 "퇴근 시간": commute.clock_out,
#                 "근무 시간": commute.work_hours,
#             }
#             for commute in result_work_data
#         ])

#         df_closed_days = pd.DataFrame([
#             {
#                 "사용자 ID": closed_day.request_user_id,
#                 "휴가 날짜": closed_day.closed_day_date,
#             }
#             for closed_day in result_closed_day
#         ])

#         # Excel 파일 생성
#         output = io.BytesIO()
#         with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#             df_users.to_excel(writer, sheet_name="사용자 정보", index=False)
#             df_commutes.to_excel(writer, sheet_name="출퇴근 기록", index=False)
#             df_closed_days.to_excel(writer, sheet_name="휴가 기록", index=False)
#         output.seek(0)

#         # 스트리밍 응답으로 Excel 파일 반환
#         return StreamingResponse(
#             output,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={
#                 "Content-Disposition": f"attachment; filename=branch_{branch_id}_commutes_report_{date}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
#             },
#         )

#     except Exception as err:
#         print(err)
#         raise HTTPException(
#             status_code=500,
#             detail="지점별 출퇴근 데이터 엑셀 파일 생성에 실패하였습니다.",
#         )


# # 출 퇴근 관리 기록 지점별 데이트 전체 조회 엑셀 다운로드
# @router.get("/{branch_id}/commutes-manager/date/excel")
# async def get_branch_all_date_commutes_manager_excel(
#     branch_id: int, date: str, token: Annotated[Users, Depends(get_current_user)]
# ):
#     try:
#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)

#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(
#             select(Commutes)
#             .join(Users)
#             .where(
#                 Users.branch_id == branch_id,
#                 Commutes.deleted_yn == "N",
#                 Commutes.clock_in >= date_start_day,
#                 Commutes.clock_in <= date_end_day,
#             )
#             .order_by(Commutes.clock_in.asc())
#         )
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(
#             select(ClosedDays)
#             .join(Users)
#             .where(
#                 Users.branch_id == branch_id,
#                 ClosedDays.deleted_yn == "N",
#                 ClosedDays.closed_day_date >= date_start_day,
#                 ClosedDays.closed_day_date <= date_end_day,
#             )
#             .options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date))
#         )
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(
#             select(Users, Branches, Parts)
#             .join(Branches, Branches.id == Users.branch_id)
#             .join(Parts, Parts.id == Users.part_id)
#             .options(
#                 load_only(Users.id, Users.name, Users.gender),
#                 load_only(Branches.name),
#                 load_only(Parts.name),
#             )
#             .distinct(Users.id)
#             .where(
#                 Users.deleted_yn == "N",
#                 Branches.id == branch_id,
#                 Branches.deleted_yn == "N",
#                 Parts.deleted_yn == "N",
#             )
#             .order_by(Users.name.asc())
#         )
#         result = find_data.fetchall()

#         # 데이터를 pandas DataFrame으로 변환
#         df_users = pd.DataFrame(
#             [
#                 {
#                     "사용자 ID": row.Users.id,
#                     "이름": row.Users.name,
#                     "성별": row.Users.gender,
#                     "부서": row.Parts.name,
#                     "지점": row.Branches.name,
#                 }
#                 for row in result
#             ]
#         )

#         df_commutes = pd.DataFrame([
#             {
#                 "사용자 ID": commute.request_user_id,
#                 "출근 시간": commute.clock_in,
#                 "퇴근 시간": commute.clock_out,
#                 "근무 시간": commute.work_hours,
#             }
#             for commute in result_work_data
#         ])

#         df_closed_days = pd.DataFrame([
#             {
#                 "사용자 ID": closed_day.request_user_id,
#                 "휴가 날짜": closed_day.closed_day_date,
#             }
#             for closed_day in result_closed_day
#         ])

#         # Excel 파일 생성
#         output = io.BytesIO()
#         with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#             df_users.to_excel(writer, sheet_name="사용자 정보", index=False)
#             df_commutes.to_excel(writer, sheet_name="출퇴근 기록", index=False)
#             df_closed_days.to_excel(writer, sheet_name="휴가 기록", index=False)
#         output.seek(0)

#         # 스트리밍 응답으로 Excel 파일 반환
#         return StreamingResponse(
#             output,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={
#                 "Content-Disposition": f"attachment; filename=branch_{branch_id}_commutes_report_{date}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
#             },
#         )

#     except Exception as err:
#         print(err)
#         raise HTTPException(
#             status_code=500,
#             detail="지점별 출퇴근, 휴가 데이터 및 사용자 정보 엑셀 파일 생성에 실패하였습니다.",
#         )


# # 출 퇴근 관리 기록 파트별 전체 조회 엑셀 다운로드
# @router.get("/{branch_id}/parts/{part_id}/commutes-manager/excel")
# async def get_part_all_commutes_manager_excel(
#     branch_id: int, part_id: int, token: Annotated[Users, Depends(get_current_user)]
# ):
#     try:

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(
#             select(Commutes)
#             .where(
#                 Users.branch_id == branch_id,
#                 Users.part_id == part_id,
#                 Commutes.deleted_yn == "N",
#             )
#             .order_by(Commutes.clock_in.asc())
#         )
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(
#             select(ClosedDays)
#             .where(ClosedDays.deleted_yn == "N")
#             .options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date))
#         )
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(
#             select(Users, Branches, Parts)
#             .join(Branches, Branches.id == Users.branch_id)
#             .join(Parts, Parts.id == Users.part_id)
#             .options(
#                 load_only(Users.id, Users.name, Users.gender),
#                 load_only(Branches.name),
#                 load_only(Parts.name),
#             )
#             .distinct(Users.id)
#             .where(
#                 Users.deleted_yn == "N",
#                 Branches.id == branch_id,
#                 Branches.deleted_yn == "N",
#                 Parts.id == part_id,
#                 Parts.deleted_yn == "N",
#                 Commutes.deleted_yn == "N",
#             )
#             .order_by(Users.name.asc())
#         )
#         result = find_data.fetchall()

#         # 데이터를 pandas DataFrame으로 변환
#         df_users = pd.DataFrame(
#             [
#                 {
#                     "사용자 ID": row.Users.id,
#                     "이름": row.Users.name,
#                     "성별": row.Users.gender,
#                     "부서": row.Parts.name,
#                     "지점": row.Branches.name,
#                 }
#                 for row in result
#             ]
#         )

#         df_commutes = pd.DataFrame([
#             {
#                 "사용자 ID": commute.request_user_id,
#                 "출근 시간": commute.clock_in,
#                 "퇴근 시간": commute.clock_out,
#                 "근무 시간": commute.work_hours,
#             }
#             for commute in result_work_data
#         ])

#         df_closed_days = pd.DataFrame([
#             {
#                 "사용자 ID": closed_day.request_user_id,
#                 "휴가 날짜": closed_day.closed_day_date,
#             }
#             for closed_day in result_closed_day
#         ])

#         # Excel 파일 생성
#         output = io.BytesIO()
#         with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#             df_users.to_excel(writer, sheet_name="사용자 정보", index=False)
#             df_commutes.to_excel(writer, sheet_name="출퇴근 기록", index=False)
#             df_closed_days.to_excel(writer, sheet_name="휴가 기록", index=False)
#         output.seek(0)

#         # 스트리밍 응답으로 Excel 파일 반환
#         return StreamingResponse(
#             output,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={
#                 "Content-Disposition": f"attachment; filename=branch_{branch_id}_part_{part_id}_commutes_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
#             },
#         )

#     except Exception as err:
#         print(err)
#         raise HTTPException(
#             status_code=500,
#             detail="지점 및 부서별 출퇴근 데이터 엑셀 파일 생성에 실패하였습니다.",
#         )


# # 출 퇴근 관리 기록 파트별 데이트 전체 조회 엑셀 다운로드
# @router.get("/{branch_id}/parts/{part_id}/commutes-manager/date/excel")
# async def get_branch_part_all_date_commutes_manager_excel(
#     branch_id: int,
#     part_id: int,
#     date: str,
#     token: Annotated[Users, Depends(get_current_user)],
# ):
#     try:
#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)

#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(
#             select(Commutes)
#             .join(Users)
#             .where(
#                 Users.branch_id == branch_id,
#                 Users.part_id == part_id,
#                 Commutes.deleted_yn == "N",
#                 Commutes.clock_in >= date_start_day,
#                 Commutes.clock_in <= date_end_day,
#             )
#             .order_by(Commutes.clock_in.asc())
#         )
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(
#             select(ClosedDays)
#             .join(Users)
#             .where(
#                 Users.branch_id == branch_id,
#                 Users.part_id == part_id,
#                 ClosedDays.deleted_yn == "N",
#                 ClosedDays.closed_day_date >= date_start_day,
#                 ClosedDays.closed_day_date <= date_end_day,
#             )
#             .options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date))
#         )
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(
#             select(Users, Branches, Parts)
#             .join(Branches, Branches.id == Users.branch_id)
#             .join(Parts, Parts.id == Users.part_id)
#             .options(
#                 load_only(Users.id, Users.name, Users.gender),
#                 load_only(Branches.name),
#                 load_only(Parts.name),
#             )
#             .distinct(Users.id)
#             .where(
#                 Users.deleted_yn == "N",
#                 Branches.id == branch_id,
#                 Branches.deleted_yn == "N",
#                 Parts.id == part_id,
#                 Parts.deleted_yn == "N",
#             )
#             .order_by(Users.name.asc())
#         )
#         result = find_data.fetchall()

#         # 데이터를 pandas DataFrame으로 변환
#         df_users = pd.DataFrame(
#             [
#                 {
#                     "사용자 ID": row.Users.id,
#                     "이름": row.Users.name,
#                     "성별": row.Users.gender,
#                     "부서": row.Parts.name,
#                     "지점": row.Branches.name,
#                 }
#                 for row in result
#             ]
#         )

#         df_commutes = pd.DataFrame([
#             {
#                 "사용자 ID": commute.request_user_id,
#                 "출근 시간": commute.clock_in,
#                 "퇴근 시간": commute.clock_out,
#                 "근무 시간": commute.work_hours,
#             }
#             for commute in result_work_data
#         ])

#         df_closed_days = pd.DataFrame([
#             {
#                 "사용자 ID": closed_day.request_user_id,
#                 "휴가 날짜": closed_day.closed_day_date,
#             }
#             for closed_day in result_closed_day
#         ])

#         # Excel 파일 생성
#         output = io.BytesIO()
#         with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#             df_users.to_excel(writer, sheet_name="사용자 정보", index=False)
#             df_commutes.to_excel(writer, sheet_name="출퇴근 기록", index=False)
#             df_closed_days.to_excel(writer, sheet_name="휴가 기록", index=False)
#         output.seek(0)

#         # 스트리밍 응답으로 Excel 파일 반환
#         return StreamingResponse(
#             output,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={
#                 "Content-Disposition": f"attachment; filename=branch_{branch_id}_part_{part_id}_commutes_report_{date}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
#             },
#         )

#     except Exception as err:
#         print(err)
#         raise HTTPException(
#             status_code=500,
#             detail="지점별 출퇴근, 휴가 데이터 및 사용자 정보 엑셀 파일 생성에 실패하였습니다.",
#         )
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from typing import Annotated, Optional
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.closed_days.closed_days_model import ClosedDays
from app.models.users.users_model import Users
from app.models.parts.parts_model import Parts
from app.models.commutes.commutes_model import Commutes
from app.models.branches.branches_model import Branches
from app.models.branches.work_policies_model import WorkPolicies
from sqlalchemy.future import select
from sqlalchemy.orm import load_only
from sqlalchemy import or_
from datetime import datetime
from calendar import monthrange
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io


router = APIRouter(dependencies=[Depends(validate_token)])
commutes_manager = async_session()


""" 출퇴근 관리 기록 조회 """

@router.get('/commutes-manager')
async def get_commutes_manager(
    token: Annotated[Users, Depends(get_current_user)],
    year_month: Optional[str] = Query(None, description="YYYY-MM 형식의 년월"),
    branch: Optional[int] = Query(None, description="지점 ID"),
    part: Optional[int] = Query(None, description="파트 ID"),
    name: Optional[str] = Query(None, description="사용자 이름"),
    phone_number: Optional[str] = Query(None, description="전화번호")
):
    try:
        base_query = (
            select(
                Users.id.label('user_id'),
                Users.name.label('user_name'),
                Users.gender.label('user_gender'),
                Users.phone_number.label('phone_number'),
                Branches.id.label('branch_id'),
                Branches.name.label('branch_name'),
                Parts.id.label('part_id'),
                Parts.name.label('part_name'),
                WorkPolicies.weekly_work_days,
                Commutes.clock_in,
                Commutes.clock_out
            )
            .join(Branches, Users.branch_id == Branches.id)
            .join(Parts, Users.part_id == Parts.id)
            .join(WorkPolicies, Branches.id == WorkPolicies.branch_id)
            .outerjoin(Commutes, Users.id == Commutes.user_id)
        )


        # 년월 필터링 (기존 코드와 동일)
        if year_month:
            try:
                date_obj = datetime.strptime(year_month, "%Y-%m")
                year = date_obj.year
                month = date_obj.month
                days_in_month = monthrange(year, month)[1]
                start_date = datetime(year, month, 1)
                end_date = datetime(year, month, days_in_month, 23, 59, 59)
                
                base_query = base_query.where(
                    Commutes.clock_in >= start_date,
                    Commutes.clock_in <= end_date
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="올바른 년월 형식이 아닙니다. (YYYY-MM)")

        # 필터 조건 추가
        if branch:
            base_query = base_query.where(Branches.id == branch)
            if part:
                base_query = base_query.where(Parts.id == part)
        if name:
            base_query = base_query.where(Users.name==name)
        if phone_number:
            base_query = base_query.where(Users.phone_number==phone_number)
        
        
        # 삭제되지 않은 레코드만 조회
        final_query = base_query.where(
            Users.deleted_yn == "N",
            Branches.deleted_yn == "N",
            Parts.deleted_yn == "N",
            or_(Commutes.deleted_yn == "N", Commutes.deleted_yn == None)
        ).order_by(Users.id, Commutes.clock_in)

        result = await commutes_manager.execute(final_query)
        records = result.fetchall()

        formatted_data = []
        current_user = None
        user_data = None

        for record in records:
            if current_user != record.user_id:
                if user_data:
                    formatted_data.append(user_data)
                
                user_data = {
                    "user_id": record.user_id,
                    "branch_name": record.branch_name,
                    "user_name": record.user_name,
                    "user_gender": record.user_gender,
                    "phone_number": record.phone_number,
                    "parts": {
                        "part_id": record.part_id,
                        "part_name": record.part_name,
                        "weekly_work_days": record.weekly_work_days
                    }
                }
                
                if year_month:
                    for day in range(1, days_in_month + 1):
                        user_data[f"{day}day"] = {"check_in": None, "check_out": None}
                
                current_user = record.user_id

            if record.clock_in:
                day = record.clock_in.day
                user_data[f"{day}day"] = {
                    "check_in": record.clock_in.strftime("%H:%M"),
                    "check_out": record.clock_out.strftime("%H:%M") if record.clock_out else None
                }

        if user_data:
            formatted_data.append(user_data)

        return {
            "message": "성공적으로 출퇴근 정보를 조회하였습니다.",
            "data": formatted_data
        }

    except Exception as err:
        print(f"Error: {str(err)}")
        raise HTTPException(status_code=500, detail="출퇴근 데이터 조회에 실패하였습니다.")



""" 유틸 """

# @router.get('/commutes-manager/excel')
# async def get_all_commutes_manager_excel(token: Annotated[Users, Depends(get_current_user)]):
#     try:
#         # ... existing query code ...
#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(select(Commutes).where(Commutes.deleted_yn == "N").order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)))
#         result_closed_day = find_closed_day.scalars().all()
        
#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N").order_by(Users.name.asc()))
#         result = find_data.fetchall()

#         # DataFrame 생성 (encoding 옵션 제거)
#         df_users = pd.DataFrame([
#             {
#                 "사용자 ID": row.Users.id,
#                 "이름": row.Users.name,
#                 "성별": row.Users.gender,
#                 "부서": row.Parts.name,
#                 "지점": row.Branches.name,
#             }
#             for row in result
#         ])

#         df_commutes = pd.DataFrame([
#             {
#                 "사용자 ID": commute.user_id,
#                 "출근 시간": commute.clock_in,
#                 "퇴근 시간": commute.clock_out,
#                 "근무 시간": commute.work_hours,
#             }
#             for commute in result_work_data
#         ])

#         df_closed_days = pd.DataFrame([
#             {
#                 "사용자 ID": closed_day.user_id,
#                 "휴가 날짜": closed_day.closed_day_date,
#             }
#             for closed_day in result_closed_day
#         ])
        

#         # Excel 파일 생성 시 인코딩 및 폰트 설정
#         output = io.BytesIO()
#         with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#             workbook = writer.book
#             # 기본 폰트를 한글 지원 폰트로 설정
#             workbook.formats[0].set_font_name('맑은 고딕')
            
#             # 각 시트에 데이터 쓰기
#             df_users.to_excel(writer, sheet_name='사용자 정보', index=False)
#             df_commutes.to_excel(writer, sheet_name='출퇴근 기록', index=False)
#             df_closed_days.to_excel(writer, sheet_name='휴가 기록', index=False)

#         output.seek(0)

#         # 파일명에 한글 처리를 위한 인코딩 추가
#         filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_commutes_report.xlsx"
#         encoded_filename = filename.encode('utf-8')

#         return StreamingResponse(
#             output,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             headers={
#                 "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename.decode('utf-8')}"
#             }
#         )

#     except Exception as err:
#         print(f"Error: {str(err)}")
#         raise HTTPException(status_code=500, detail="출퇴근 데이터 엑셀 파일 생성에 실패하였습니다.")
    
    
    
    

# 출 퇴근 관리 기록 전체 조회 엑셀 다운로드
@router.get('/commutes-manager/excel')
async def get_all_commutes_manager_excel(token: Annotated[Users, Depends(get_current_user)]):
    try:

        # 유저 출 퇴근 시간 조회
        find_work_data = await commutes_manager.execute(select(Commutes).where(Commutes.deleted_yn == "N").order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()

        # 유저 휴가 조회
        find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)))
        result_closed_day = find_closed_day.scalars().all()
        
        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N").order_by(Users.name.asc()))
        result = find_data.fetchall()

        # 데이터를 pandas DataFrame으로 변환
        df_users = pd.DataFrame([
            {
                "사용자 ID": row.Users.id,
                "이름": row.Users.name,
                "성별": row.Users.gender,
                "부서": row.Parts.name,
                "지점": row.Branches.name,
            }
            for row in result
        ])

        df_commutes = pd.DataFrame([
            {
                "사용자 ID": commute.user_id,
                "출근 시간": commute.clock_in,
                "퇴근 시간": commute.clock_out,
                "근무 시간": commute.work_hours,
            }
            for commute in result_work_data
        ])

        df_closed_days = pd.DataFrame([
            {
                "사용자 ID": closed_day.user_id,
                "휴가 날짜": closed_day.closed_day_date,
            }
            for closed_day in result_closed_day
        ])

        # Excel 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_users.to_excel(writer, sheet_name='사용자 정보', index=False)
            df_commutes.to_excel(writer, sheet_name='출퇴근 기록', index=False)
            df_closed_days.to_excel(writer, sheet_name='휴가 기록', index=False)
        output.seek(0)

        # 스트리밍 응답으로 Excel 파일 반환
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=commutes_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"}
        )

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="출퇴근 데이터 엑셀 파일 생성에 실패하였습니다.")
    

# 출 퇴근 관리 기록 date로 전체 조회 엑셀 다운로드
@router.get('/commutes-manager/date/excel')
async def get_all_date_commutes_manager_excel(date: str, token: Annotated[Users, Depends(get_current_user)]):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        # 유저 출 퇴근 시간 조회
        find_work_data = await commutes_manager.execute(select(Commutes).join(Users).where(Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()

        # 유저 휴가 조회
        find_closed_day = await commutes_manager.execute(select(ClosedDays).join(Users).where(ClosedDays.deleted_yn == "N", ClosedDays.closed_day_date >= date_start_day, ClosedDays.closed_day_date <= date_end_day).options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)))
        result_closed_day = find_closed_day.scalars().all()

        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N").order_by(Users.name.asc()))
        result = find_data.fetchall()

        # 데이터를 pandas DataFrame으로 변환
        df_users = pd.DataFrame([
            {
                "사용자 ID": row.Users.id,
                "이름": row.Users.name,
                "성별": row.Users.gender,
                "부서": row.Parts.name,
                "지점": row.Branches.name,
            }
            for row in result
        ])

        df_commutes = pd.DataFrame([
            {
                "사용자 ID": commute.user_id,
                "출근 시간": commute.clock_in,
                "퇴근 시간": commute.clock_out,
                "근무 시간": commute.work_hours,
            }
            for commute in result_work_data
        ])

        df_closed_days = pd.DataFrame([
            {
                "사용자 ID": closed_day.user_id,
                "휴가 날짜": closed_day.closed_day_date,
            }
            for closed_day in result_closed_day
        ])

        # Excel 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_users.to_excel(writer, sheet_name='사용자 정보', index=False)
            df_commutes.to_excel(writer, sheet_name='출퇴근 기록', index=False)
            df_closed_days.to_excel(writer, sheet_name='휴가 기록', index=False)
        output.seek(0)

        # 스트리밍 응답으로 Excel 파일 반환
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=all_commutes_report_{date}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"}
        )

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="날짜별 전체 출퇴근, 휴가 데이터 및 사용자 정보 엑셀 파일 생성에 실패하였습니다.")
    

# 출 퇴근 관리 기록 지점별 전체 조회 엑셀 다운로드
@router.get('/{branch_id}/commutes-manager/excel')
async def get_branch_all_commutes_manager_excel(branch_id: int, date: str, token: Annotated[Users, Depends(get_current_user)]):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        # 유저 출 퇴근 시간 조회
        find_work_data = await commutes_manager.execute(select(Commutes).where(Users.branch_id == branch_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()

        # 유저 휴가 조회
        find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)))
        result_closed_day = find_closed_day.scalars().all()

        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()))
        result = find_data.fetchall()

        # 데이터를 pandas DataFrame으로 변환
        df_users = pd.DataFrame([
            {
                "사용자 ID": row.Users.id,
                "이름": row.Users.name,
                "성별": row.Users.gender,
                "부서": row.Parts.name,
                "지점": row.Branches.name,
            }
            for row in result
        ])

        df_commutes = pd.DataFrame([
            {
                "사용자 ID": commute.user_id,
                "출근 시간": commute.clock_in,
                "퇴근 시간": commute.clock_out,
                "근무 시간": commute.work_hours,
            }
            for commute in result_work_data
        ])

        df_closed_days = pd.DataFrame([
            {
                "사용자 ID": closed_day.user_id,
                "휴가 날짜": closed_day.closed_day_date,
            }
            for closed_day in result_closed_day
        ])

        # Excel 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_users.to_excel(writer, sheet_name='사용자 정보', index=False)
            df_commutes.to_excel(writer, sheet_name='출퇴근 기록', index=False)
            df_closed_days.to_excel(writer, sheet_name='휴가 기록', index=False)
        output.seek(0)

        # 스트리밍 응답으로 Excel 파일 반환
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=branch_{branch_id}_commutes_report_{date}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"}
        )

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="지점별 출퇴근 데이터 엑셀 파일 생성에 실패하였습니다.")
    

# 출 퇴근 관리 기록 지점별 데이트 전체 조회 엑셀 다운로드
@router.get('/{branch_id}/commutes-manager/date/excel')
async def get_branch_all_date_commutes_manager_excel(branch_id: int, date: str, token: Annotated[Users, Depends(get_current_user)]):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        # 유저 출 퇴근 시간 조회
        find_work_data = await commutes_manager.execute(select(Commutes).join(Users).where(Users.branch_id == branch_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()

        # 유저 휴가 조회
        find_closed_day = await commutes_manager.execute(select(ClosedDays).join(Users).where(Users.branch_id == branch_id, ClosedDays.deleted_yn == "N", ClosedDays.closed_day_date >= date_start_day, ClosedDays.closed_day_date <= date_end_day).options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)))
        result_closed_day = find_closed_day.scalars().all()

        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N").order_by(Users.name.asc()))
        result = find_data.fetchall()

        # 데이터를 pandas DataFrame으로 변환
        df_users = pd.DataFrame([
            {
                "사용자 ID": row.Users.id,
                "이름": row.Users.name,
                "성별": row.Users.gender,
                "부서": row.Parts.name,
                "지점": row.Branches.name,
            }
            for row in result
        ])

        df_commutes = pd.DataFrame([
            {
                "사용자 ID": commute.user_id,
                "출근 시간": commute.clock_in,
                "퇴근 시간": commute.clock_out,
                "근무 시간": commute.work_hours,
            }
            for commute in result_work_data
        ])

        df_closed_days = pd.DataFrame([
            {
                "사용자 ID": closed_day.user_id,
                "휴가 날짜": closed_day.closed_day_date,
            }
            for closed_day in result_closed_day
        ])

        # Excel 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_users.to_excel(writer, sheet_name='사용자 정보', index=False)
            df_commutes.to_excel(writer, sheet_name='출퇴근 기록', index=False)
            df_closed_days.to_excel(writer, sheet_name='휴가 기록', index=False)
        output.seek(0)

        # 스트리밍 응답으로 Excel 파일 반환
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=branch_{branch_id}_commutes_report_{date}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"}
        )

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="지점별 출퇴근, 휴가 데이터 및 사용자 정보 엑셀 파일 생성에 실패하였습니다.")
    

# 출 퇴근 관리 기록 파트별 전체 조회 엑셀 다운로드
@router.get('/{branch_id}/parts/{part_id}/commutes-manager/excel')
async def get_part_all_commutes_manager_excel(branch_id: int, part_id: int, token: Annotated[Users, Depends(get_current_user)]):
    try:

        # 유저 출 퇴근 시간 조회
        find_work_data = await commutes_manager.execute(select(Commutes).where(Users.branch_id == branch_id, Users.part_id == part_id, Commutes.deleted_yn == "N").order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()

        # 유저 휴가 조회
        find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)))
        result_closed_day = find_closed_day.scalars().all()

        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Commutes.deleted_yn == "N").order_by(Users.name.asc()))
        result = find_data.fetchall()

        # 데이터를 pandas DataFrame으로 변환
        df_users = pd.DataFrame([
            {
                "사용자 ID": row.Users.id,
                "이름": row.Users.name,
                "성별": row.Users.gender,
                "부서": row.Parts.name,
                "지점": row.Branches.name,
            }
            for row in result
        ])

        df_commutes = pd.DataFrame([
            {
                "사용자 ID": commute.user_id,
                "출근 시간": commute.clock_in,
                "퇴근 시간": commute.clock_out,
                "근무 시간": commute.work_hours,
            }
            for commute in result_work_data
        ])

        df_closed_days = pd.DataFrame([
            {
                "사용자 ID": closed_day.user_id,
                "휴가 날짜": closed_day.closed_day_date,
            }
            for closed_day in result_closed_day
        ])

        # Excel 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_users.to_excel(writer, sheet_name='사용자 정보', index=False)
            df_commutes.to_excel(writer, sheet_name='출퇴근 기록', index=False)
            df_closed_days.to_excel(writer, sheet_name='휴가 기록', index=False)
        output.seek(0)

        # 스트리밍 응답으로 Excel 파일 반환
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=branch_{branch_id}_part_{part_id}_commutes_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"}
        )

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="지점 및 부서별 출퇴근 데이터 엑셀 파일 생성에 실패하였습니다.")
    

# 출 퇴근 관리 기록 파트별 데이트 전체 조회 엑셀 다운로드
@router.get('/{branch_id}/parts/{part_id}/commutes-manager/date/excel')
async def get_branch_part_all_date_commutes_manager_excel(branch_id: int, part_id: int, date: str, token: Annotated[Users, Depends(get_current_user)]):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        # 유저 출 퇴근 시간 조회
        find_work_data = await commutes_manager.execute(select(Commutes).join(Users).where(Users.branch_id == branch_id, Users.part_id == part_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
        result_work_data = find_work_data.scalars().all()

        # 유저 휴가 조회
        find_closed_day = await commutes_manager.execute(select(ClosedDays).join(Users).where(Users.branch_id == branch_id, Users.part_id == part_id, ClosedDays.deleted_yn == "N", ClosedDays.closed_day_date >= date_start_day, ClosedDays.closed_day_date <= date_end_day).options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)))
        result_closed_day = find_closed_day.scalars().all()

        find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N").order_by(Users.name.asc()))
        result = find_data.fetchall()

        # 데이터를 pandas DataFrame으로 변환
        df_users = pd.DataFrame([
            {
                "사용자 ID": row.Users.id,
                "이름": row.Users.name,
                "성별": row.Users.gender,
                "부서": row.Parts.name,
                "지점": row.Branches.name,
            }
            for row in result
        ])

        df_commutes = pd.DataFrame([
            {
                "사용자 ID": commute.user_id,
                "출근 시간": commute.clock_in,
                "퇴근 시간": commute.clock_out,
                "근무 시간": commute.work_hours,
            }
            for commute in result_work_data
        ])

        df_closed_days = pd.DataFrame([
            {
                "사용자 ID": closed_day.user_id,
                "휴가 날짜": closed_day.closed_day_date,
            }
            for closed_day in result_closed_day
        ])

        # Excel 파일 생성
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_users.to_excel(writer, sheet_name='사용자 정보', index=False)
            df_commutes.to_excel(writer, sheet_name='출퇴근 기록', index=False)
            df_closed_days.to_excel(writer, sheet_name='휴가 기록', index=False)
        output.seek(0)

        # 스트리밍 응답으로 Excel 파일 반환
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=branch_{branch_id}_part_{part_id}_commutes_report_{date}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"}
        )

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="지점별 출퇴근, 휴가 데이터 및 사용자 정보 엑셀 파일 생성에 실패하였습니다.")




"""이전 코드"""

# # 출근 퇴근 관리 전체 조회 [어드민만 가능]
# @router.get('/commutes-manager')
# async def get_commutes_manager(token : Annotated[Users, Depends(get_current_user)]):
#     try:
#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(select(Commutes).where(Commutes.deleted_yn == "N").order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)).offset(0).limit(100))
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
#         result = find_data.fetchall() 

#         formatted_data = [
#             {
#                 "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
#                 "part": {"name": row.Parts.name},
#                 "branch": {"name": row.Branches.name},
#             }
#             for row in result
#         ]

#         return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "commutes" : result_work_data, "closed_days" : result_closed_day}
        
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="출 퇴근 데이터 전체 조회에 실패하였습니다.")
    

# # 출근 퇴근 관리 월별 전체 조회 [어드민만 가능]
# @router.get('/commutes-manager/date')
# async def get_all_date_commutes_manager(date : str, token : Annotated[Users, Depends(get_current_user)]):
#     try:

#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)
        
#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(select(Commutes).where(Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)).offset(0).limit(100))
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
#         result = find_data.fetchall() 

#         formatted_data = [
#             {
#                 "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
#                 "part": {"name": row.Parts.name},
#                 "branch": {"name": row.Branches.name},
#             }
#             for row in result
#         ]

#         return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "commutes" : result_work_data, "closed_days" : result_closed_day}
        
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="출 퇴근 데이터 전체 조회에 실패하였습니다.")


# """ 지점별 조회 """

# # 출근 퇴근 관리 지점별 전체 조회 [최고 어드민만 가능]
# @router.get('/{branch_id}/commutes-manager')
# async def get_branch_all_commutes_manager(branch_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
#     try:

#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)
        
#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회    
#         find_work_data = await commutes_manager.execute(select(Commutes).where(Users.branch_id == branch_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)).offset(0).limit(100))
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
#         result = find_data.fetchall() 

#         formatted_data = [
#             {
#                 "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
#                 "part": {"name": row.Parts.name},
#                 "branch": {"name": row.Branches.name},
#             }
#             for row in result
#         ]

#         return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "commutes" : result_work_data, "closed_days" : result_closed_day}
        
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="출 퇴근 데이터 전체 조회에 실패하였습니다.")

# # 출근 퇴근 관리 지점별 조회 [어드민만 가능]
# @router.get('/{branch_id}/commutes-manager/date')
# async def get_branch_all_date_commutes_manager(branch_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
#     try:

#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)
        
#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(select(Commutes).where(Users.branch_id == branch_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)).offset(0).limit(100))
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
#         result = find_data.fetchall() 

#         formatted_data = [
#             {
#                 "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
#                 "part": {"name": row.Parts.name},
#                 "branch": {"name": row.Branches.name},
#             }
#             for row in result
#         ]

#         return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "commutes" : result_work_data, "closed_days" : result_closed_day}
        
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="출 퇴근 데이터 전체 조회에 실패하였습니다.")
    



# # 출근 퇴근 관리 지점 유저 이름별 조회 [어드민만 가능]
# @router.get('/{branch_id}/commutes-manager/date/name')
# async def get_branch_name_commutes_manager(branch_id : int, name : str, date : str, token : Annotated[Users, Depends(get_current_user)]):
#     try:

#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)
        
#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회    
#         find_work_data = await commutes_manager.execute(select(Commutes).join(Users, Users.id == Commutes.user_id).options(load_only(Commutes.id, Commutes.clock_in, Commutes.clock_out, Commutes.work_hours)).where(Users.name.like(f"%{name}%"), Users.branch_id == branch_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)).offset(0).limit(100))
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.name.like(f"%{name}%"), Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
#         result = find_data.fetchall() 

#         formatted_data = [
#             {
#                 "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
#                 "part": {"name": row.Parts.name},
#                 "branch": {"name": row.Branches.name},
#             }
#             for row in result
#         ]

#         return {"message" : "성공적으로 출근, 퇴근정보를 이름 필터 조회 하였습니다.", "data" : formatted_data, "commutes" : result_work_data, "closed_days" : result_closed_day}
        
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="출 퇴근 데이터 이름으로 조회에 실패하였습니다.")


# # 출근 퇴근 관리 지점 유저 전화번호 조회 [어드민만 가능]
# @router.get('/{branch_id}/commutes-manager/date/phonenumber')
# async def get_branch_phonenumber_commutes_manager(branch_id : int, phonenumber : str, date : str, token : Annotated[Users, Depends(get_current_user)]):
#     try:

#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)
        
#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(select(Commutes).join(Users, Users.id == Commutes.user_id).options(load_only(Commutes.id, Commutes.clock_in, Commutes.clock_out, Commutes.work_hours)).where(Users.phone_number.like(f"%{phonenumber}%"), Users.branch_id == branch_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)).offset(0).limit(100))
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.phone_number.like(f"%{phonenumber}%"), Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
#         result = find_data.fetchall() 

#         formatted_data = [
#             {
#                 "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
#                 "part": {"name": row.Parts.name},
#                 "branch": {"name": row.Branches.name},
#             }
#             for row in result
#         ]

#         return {"message" : "성공적으로 출근, 퇴근 정보를 번호 조회로 하였습니다.", "data" : formatted_data, "commutes" : result_work_data, "closed_days" : result_closed_day}
        
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="출 퇴근 데이터 번호로 조화에 실패하였습니다.")
    


# """ 파트별 조회 """   

# # 출근 퇴근 관리 파트 전체 조회 [어드민만 가능]
# @router.get('/{branch_id}/parts/{part_id}/commutes-manager')
# async def get_part_all_date_commutes_manager(branch_id : int, part_id : int, token : Annotated[Users, Depends(get_current_user)]):
#     try:

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(select(Commutes).where(Users.branch_id == branch_id, Users.part_id == part_id, Commutes.deleted_yn == "N").order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)).offset(0).limit(100))
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
#         result = find_data.fetchall() 

#         formatted_data = [
#             {
#                 "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
#                 "part": {"name": row.Parts.name},
#                 "branch": {"name": row.Branches.name},
#             }
#             for row in result
#         ]

#         return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "commutes" : result_work_data, "closed_days" : result_closed_day}
        
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="출 퇴근 데이터 파트 전체 조회에 실패하였습니다.")

# # 출근 퇴근 관리 파트 월별 전체 조회 [어드민만 가능]
# @router.get('/{branch_id}/parts/{part_id}/commutes-manager/date')
# async def get_part_all_date_commutes_manager(branch_id : int, part_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
#     try:

#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)
        
#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(select(Commutes).where(Commutes.deleted_yn == "N", Users.branch_id == branch_id, Users.part_id == part_id, Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)).offset(0).limit(100))
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
#         result = find_data.fetchall() 

#         formatted_data = [
#             {
#                 "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
#                 "part": {"name": row.Parts.name},
#                 "branch": {"name": row.Branches.name},
#             }
#             for row in result
#         ]

#         return {"message" : "성공적으로 출근, 퇴근 정보를 전체 조회를 하였습니다.", "data" : formatted_data, "commutes" : result_work_data, "closed_days" : result_closed_day}
        
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="출 퇴근 데이터 파트 전체 조회에 실패하였습니다.")


# # 출근 퇴근 관리 파트 유저 이름별 조회
# @router.get('/{branch_id}/parts/{part_id}/commutes-manager/date/name')
# async def get_part_name_commutes_manager(branch_id : int, part_id : int, name : str, date : str, token : Annotated[Users, Depends(get_current_user)]):
#     try:

#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)
        
#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(select(Commutes).join(Users, Users.id == Commutes.user_id).options(load_only(Commutes.id, Commutes.clock_in, Commutes.clock_out, Commutes.work_hours)).where(Users.name.like(f"%{name}%"), Users.branch_id == branch_id, Users.part_id == part_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)).offset(0).limit(100))
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.name.like(f"%{name}%"), Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
#         result = find_data.fetchall() 

#         formatted_data = [
#             {
#                 "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
#                 "part": {"name": row.Parts.name},
#                 "branch": {"name": row.Branches.name},
#             }
#             for row in result
#         ]

#         return {"message" : "성공적으로 출근, 퇴근정보를 이름 필터 조회 하였습니다.", "data" : formatted_data, "commutes" : result_work_data, "closed_days" : result_closed_day}
        
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="출 퇴근 데이터 이름으로 조회에 실패하였습니다.")



# # 출근 퇴근 관리 파트 유저 전화번호 조회
# @router.get('/{branch_id}/parts/{part_id}/commutes-manager/date/phonenumber')
# async def get_part_phonenumber_commutes_manager(branch_id : int, part_id : int, phonenumber : str, date : str, token : Annotated[Users, Depends(get_current_user)]):
#     try:

#         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         date_start_day = date_obj.replace(day=1)
        
#         _, last_day = monthrange(date_obj.year, date_obj.month)
#         date_end_day = date_obj.replace(day=last_day)

#         # 유저 출 퇴근 시간 조회
#         find_work_data = await commutes_manager.execute(select(Commutes).join(Users, Users.id == Commutes.user_id).options(load_only(Commutes.id, Commutes.clock_in, Commutes.clock_out, Commutes.work_hours)).where(Users.phone_number.like(f"%{phonenumber}%"), Users.branch_id == branch_id, Users.part_id == part_id, Commutes.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day).order_by(Commutes.clock_in.asc()))
#         result_work_data = find_work_data.scalars().all()

#         # 유저 휴가 조회
#         find_closed_day = await commutes_manager.execute(select(ClosedDays).where(ClosedDays.deleted_yn == "N").options(load_only(ClosedDays.user_id, ClosedDays.closed_day_date)).offset(0).limit(100))
#         result_closed_day = find_closed_day.scalars().all()

#         find_data = await commutes_manager.execute(select(Users, Branches, Parts).join(Branches, Branches.id == Users.branch_id).join(Parts, Parts.id == Users.part_id).options(load_only(Users.id, Users.name, Users.gender), load_only(Branches.name), load_only(Parts.name)).distinct(Users.id).where(Users.phone_number.like(f"%{phonenumber}%"), Users.deleted_yn == "N", Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Commutes.clock_in >= date_start_day, Commutes.clock_in <= date_end_day, Commutes.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
#         result = find_data.fetchall() 

#         formatted_data = [
#             {
#                 "user": {"id": row.Users.id, "name": row.Users.name, "gender": row.Users.gender},
#                 "part": {"name": row.Parts.name},
#                 "branch": {"name": row.Branches.name},
#             }
#             for row in result
#         ]

#         return {"message" : "성공적으로 출근, 퇴근 정보를 번호 조회로 하였습니다.", "data" : formatted_data, "commutes" : result_work_data, "closed_days" : result_closed_day}
        
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="출 퇴근 데이터 번호로 조화에 실패하였습니다.")
    

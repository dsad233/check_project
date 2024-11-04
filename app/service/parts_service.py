from sqlalchemy.ext.asyncio import AsyncSession
from app.cruds.parts import parts_crud
from app.models.parts.parts_model import Parts
from app.schemas.parts_schemas import PartRequest, PartResponse
from app.exceptions.exceptions import NotFoundError, InvalidEnumValueError, BadRequestError
from app.enums.parts import PartAutoAnnualLeaveGrant
from app.enums.branches import (LeaveResetOption, LeaveGrantOption, DecimalRoundingPolicy, AnnualLeaveDaysByYear)
from app.cruds.branches.policies import salary_polices_crud
from app.cruds.branches import branches_crud
from app.cruds.users import users_crud
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from math import floor, ceil
from app.models.branches.branches_model import Branches


async def get_part_by_id(
    *, session: AsyncSession, part_id: int
) -> Parts:
    part = await parts_crud.find_by_id(session=session, part_id=part_id)
    if part is None:
        raise NotFoundError(detail=f"{part_id}번 파트가 존재하지 않습니다.")
    return part


async def update_auto_annual_leave_grant(
    *, session: AsyncSession, part_id: int, request: str
) -> bool:
    part = await get_part_by_id(session=session, part_id=part_id)
    if part is None:
        raise NotFoundError(detail=f"{part_id}번 파트가 존재하지 않습니다.")
    if request not in PartAutoAnnualLeaveGrant:
        raise InvalidEnumValueError(f"잘못된 자동 부여 정책 ENUM 입니다: {request}")
    
    return await parts_crud.update_auto_annual_leave_grant(session=session, part_id=part_id, request=request, old=part)


async def get_parts_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> list[PartResponse]:
    parts = await parts_crud.find_all_by_branch_id(session=session, branch_id=branch_id)
    if not parts:
        return []
    return parts


async def delete_part(
    *, session: AsyncSession, part_id: int
) -> bool:
    part = await get_part_by_id(session=session, part_id=part_id)
    if part is None:
        raise NotFoundError(detail=f"{part_id}번 파트가 존재하지 않습니다.")
    return await parts_crud.delete_part(session=session, part_id=part_id)


async def update_part(
    *, session: AsyncSession, part_id: int, request: PartRequest, branch_id: int
) -> bool:
    
    part = await get_part_by_id(session=session, part_id=part_id)
    if part is None:
        raise NotFoundError(detail=f"{part_id}번 파트가 존재하지 않습니다.")
    
    if part.name != request.name:
        duplicate_part = await parts_crud.find_by_name_and_branch_id(session=session, name=request.name, branch_id=branch_id)
        if duplicate_part is not None:
            raise BadRequestError(detail=f"{request.name}은(는) 이미 존재합니다.")
    
    return await parts_crud.update_part(session=session, part_id=part_id, request=Parts(**request.model_dump(exclude_none=True)), old=part)


async def create_part(
    *, session: AsyncSession, request: PartRequest, branch_id: int
) -> PartResponse:
    duplicate_part = await parts_crud.find_by_name_and_branch_id(
        session=session, 
        name=request.name, 
        branch_id=branch_id
    )
    if duplicate_part is not None:
        raise BadRequestError(detail=f"{request.name}은(는) 이미 존재합니다.")
    
    try:
        # 파트 생성
        part = await parts_crud.create_part(
            session=session, 
            request=Parts(branch_id=branch_id, **request.model_dump())
        )
        part_id = part.id

        # 급여 템플릿 정책 생성
        if part_id:
            await salary_polices_crud.create_salary_templates_policies(
                session=session, 
                part_ids=[part_id], 
                branch_id=branch_id
            )
            await session.commit()  # 모든 변경사항 커밋
            
            # 생성된 part 객체 refresh
            await session.refresh(part)
            
            # Parts 모델을 PartResponse로 변환
            return PartResponse.model_validate(part)
            
    except Exception as e:
        await session.rollback()
        raise e


def calculate_annual_leave(work_days: int, rounding_method: DecimalRoundingPolicy) -> float:
   """
   작년 근속일수로 연차 계산
   15 * 작년 근속일수 / 365
   """
   raw_leave = (15 * work_days) / 365
   
   if rounding_method == DecimalRoundingPolicy.ROUND_UP_0_5:
       # 0.5 기준 올림 (예: 1.2 -> 1.5, 1.7 -> 2.0)
       decimal_part = raw_leave % 1
       if decimal_part == 0:
           return raw_leave
       elif decimal_part <= 0.5:
           return floor(raw_leave) + 0.5
       else:
           return ceil(raw_leave)
           
   elif rounding_method == DecimalRoundingPolicy.TRUNCATE:
       # 절삭 (예: 1.7 -> 1.0)
       return float(floor(raw_leave))
       
   elif rounding_method == DecimalRoundingPolicy.ROUND_UP:
       # 올림 (예: 1.1 -> 2.0)
       return float(ceil(raw_leave))
       
   elif rounding_method == DecimalRoundingPolicy.ROUND:
       # 반올림 (예: 1.4 -> 1.0, 1.5 -> 2.0)
       decimal = Decimal(str(raw_leave))
       rounded = float(decimal.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
       return rounded
       
   return raw_leave


async def account_based_auto_annual_leave_grant(
    *, session: AsyncSession, part: Parts, branch: Branches
) -> bool:
    """
    회계 기반 자동 연차 부여
    """
    if not branch.account_based_annual_leave_grant: # 설정 안되어있으면 종료
        return True

    leave_reset_option = branch.account_based_annual_leave_grant.account_based_january_1st
    less_than_year_option = branch.account_based_annual_leave_grant.account_based_less_than_year
    decimal_rounding_option = branch.account_based_annual_leave_grant.account_based_decimal_point
    
    today = date.today()

    if today.month == 1 and today.day == 1: # 1월 1일
        for user in part.users:
            year = relativedelta(today, user.hire_date).years # 근속년수
            remain_days = user.total_leave_days # 잔여 연차
            if year < 1: # 근속 1년 미만
                start_date = user.hire_date
                end_date = date(today.year - 1, 12, 31)
                work_days = (end_date - start_date).days + 1 # 작년 근속 일수
                grant_leave = calculate_annual_leave(work_days=work_days, rounding_method=decimal_rounding_option)
                # 1년 미만은 삭제 없음
                await users_crud.update_total_leave_days(
                    session=session,
                    user_id=user.id,
                    count=grant_leave + remain_days
                )
            else:
                grant_leave = AnnualLeaveDaysByYear.get_leave_days(year)
            
            new_leave_days = (
                grant_leave 
                if leave_reset_option == LeaveResetOption.RESET 
                else remain_days + grant_leave
            )

            await users_crud.update_total_leave_days(
                session=session,
                user_id=user.id,
                count=new_leave_days
            )

    elif today.day == 1: # 매달 1일
        for user in part.users:
            year = relativedelta(today, user.hire_date).years # 근속년수
            if year < 1: # 1년 미만 직원만
                remain_days = user.total_leave_days
                   
                # 매월 1개씩 부여
                if less_than_year_option == LeaveGrantOption.ONE_PER_MONTH:
                    # 입사 첫 달은 제외
                    if today.month != user.hire_date.month:
                        new_leave_days = remain_days + 1
                       
                        await users_crud.update_total_leave_days(
                            session=session,
                            user_id=user.id,
                            count=new_leave_days
                        )
                # 일괄부여        
                else:
                    work_days = (today - user.hire_date).days
                    if work_days <= 31: # 신규 직원이 있다면
                        new_leave_days = 11
                        
                        await users_crud.update_total_leave_days(
                            session=session,
                            user_id=user.id,
                            count=new_leave_days
                        )
            

async def entry_date_based_auto_annual_leave_grant(
    *, session: AsyncSession, part: Parts, branch: Branches
) -> bool:
    """
    입사일 기반 자동 연차 부여
    """
    if not branch.entry_date_based_annual_leave_grant: # 설정 안되어있으면 종료
        return True

    leave_reset_option = branch.entry_date_based_annual_leave_grant.entry_date_based_remaining_leave

    today = date.today()

    for user in part.users:
        year = relativedelta(today, user.hire_date).years
        remain_days = user.total_leave_days
        if today.month == user.hire_date.month and today.day == user.hire_date.day: # 오늘이 입사 년차가 갱신될때
            grant_leave = AnnualLeaveDaysByYear.get_leave_days(year)
            new_leave_days = (
                grant_leave 
                if leave_reset_option == LeaveResetOption.RESET 
                else remain_days + grant_leave
            )
            await users_crud.update_total_leave_days(
                session=session,
                user_id=user.id,
                count=new_leave_days
            )
        elif year < 1 and today.day == user.hire_date.day: # 오늘이 입사한 날짜와 같은 날일때 1년미만
            if today.month != user.hire_date.month:
                grant_leave = 1
                new_leave_days = remain_days + grant_leave

                await users_crud.update_total_leave_days(
                    session=session, 
                    user_id=user.id, 
                    count=new_leave_days
                )


async def condition_based_auto_annual_leave_grant(
    *, session: AsyncSession, part: Parts, branch: Branches
) -> bool:
    """
    조건 기반 자동 연차 부여
    """
    if not branch.condition_based_annual_leave_grant: # 설정 안되어있으면 종료
        return True

    condition_options = branch.condition_based_annual_leave_grant
    
    today = date.today()

    for condition_option in condition_options: # 조건 옵션 순회
        condition_month = condition_option.condition_based_month # 조건 월
        condition_cnt = condition_option.condition_based_cnt # 부여 일
        for user in part.users:
            if today.day == user.hire_date.day: # 입사 날짜 기준 부여
                months_worked = ( # 근속 월
                        relativedelta(today, user.hire_date).years * 12 + 
                        relativedelta(today, user.hire_date).months
                    )
                if months_worked % condition_month == 0: # 조건에 맞으면
                    remain_days = user.total_leave_days
                    await users_crud.update_total_leave_days(
                        session=session, 
                        user_id=user.id, 
                        count=remain_days + condition_cnt
                    )

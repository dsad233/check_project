from fastapi import HTTPException, logger
from sqlalchemy import case, func, select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users.users_model import Users
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.commutes.commutes_model import Commutes
from app.models.parts.hour_wage_template_model import HourWageTemplate
from app.models.users.users_work_contract_model import WorkContract
from app.models.branches.rest_days_model import RestDays

'''
파트타이머 요약 정보 목록 조회
'''
async def get_part_timer_summaries(session: AsyncSession, year: int, month: int):
    try:
        part_timer_summary_query = select(
            Users.id.label('user_id'),
            Branches.name.label('branch_name'),
            Users.name.label('user_name'),
            Parts.name.label('part_name'),
            func.count(Commutes.user_id).label('work_count')
        ).join(WorkContract, WorkContract.user_id == Users.id) \
            .filter(WorkContract.is_part_timer == True) \
            .join(Branches, Branches.id == Users.branch_id) \
            .join(Parts, Parts.id == Users.part_id) \
            .join(Commutes, Commutes.user_id == Users.id) \
            .filter(func.extract('year', Commutes.clock_in) == year) \
            .filter(func.extract('month', Commutes.clock_in) == month) \
            .group_by(Users.id, Users.name, Branches.name, Parts.name)
        
        result = await session.execute(part_timer_summary_query)
        return result.all()
    except Exception as e:
        logger.debug(e.with_traceback())
        raise HTTPException(status_code=500, detail="파트타이머 정보 목록 조회에 실패했습니다.")

'''
유저 근무 시간 및 총 급여 조회
'''
async def get_part_timer_work_hours_and_total_wage(session: AsyncSession, year: int, month: int):
    try:
        query = (
            select(
                Users.id.label('user_id'),
                func.coalesce(func.sum(
                    case(
                        (RestDays.id == None, Commutes.work_hours), 
                        else_=0
                    )
                ), 0).label('regular_work_hours'),
                func.coalesce(func.sum(
                    case(
                        (RestDays.is_paid == True, Commutes.work_hours), 
                        else_=0
                    )
                ), 0).label('holiday_work_hours'),
                func.coalesce(func.sum(Commutes.work_hours), 0).label('total_work_hours'),
                func.coalesce(func.sum(
                    case(
                        (RestDays.id == None, Commutes.work_hours * HourWageTemplate.hour_wage),
                        else_=Commutes.work_hours * 1.5
                    )
                ), 0).label('total_wage')
            )
            .join(WorkContract, WorkContract.user_id == Users.id)
            .filter(WorkContract.is_part_timer == True)
            .join(Commutes, Commutes.user_id == Users.id)
            .outerjoin(RestDays, (RestDays.date == func.date(Commutes.clock_in)) & (RestDays.branch_id == Users.branch_id))
            .join(HourWageTemplate, (HourWageTemplate.part_id == Users.part_id) & (HourWageTemplate.branch_id == Users.branch_id))
            .filter(func.extract('year', Commutes.clock_in) == year)
            .filter(func.extract('month', Commutes.clock_in) == month)
            .group_by(Users.id)
        )

        result = await session.execute(query)
        return result.all()
    except Exception as e:
        print(e)
        logger.debug(e.with_traceback())
        raise HTTPException(status_code=500, detail="근로 시간 및 급여 정보 조회에 실패했습니다.")

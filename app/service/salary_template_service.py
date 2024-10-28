from app.cruds.salary_template import salary_template_crud
from app.cruds.branches import branches_crud
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.branches.salary_template_model import SalaryTemplateDto
from app.exceptions.exceptions import NotFoundError


async def get_all_salary_template_and_allowance_policy(*, session: AsyncSession, branch_id: int) -> list[SalaryTemplateDto]:
    salary_templates = await salary_template_crud.find_all_by_branch_id(session=session, branch_id=branch_id)
    if not salary_templates:
        return []
    branch = await branches_crud.find_by_id_with_policies(session=session, branch_id=branch_id)

    return [SalaryTemplateDto(id=salary_template.id,
                              part_id=salary_template.part_id,
                              name=salary_template.name,
                              part_name=salary_template.part.name,
                              is_january_entry=salary_template.is_january_entry,
                              weekly_work_days=salary_template.weekly_work_days,
                              month_salary=salary_template.month_salary,
                              included_holiday_allowance=salary_template.included_holiday_allowance,
                              included_job_allowance=salary_template.included_job_allowance,
                              hour_wage=salary_template.hour_wage,
                              basic_salary=salary_template.basic_salary,
                              contractual_working_hours=salary_template.contractual_working_hours,
                              weekly_rest_hours=salary_template.weekly_rest_hours,
                              annual_salary=salary_template.annual_salary,
                              comprehensive_overtime_allowance=salary_template.comprehensive_overtime_allowance,
                              comprehensive_overtime_hour=salary_template.comprehensive_overtime_hour,
                              annual_leave_allowance=salary_template.annual_leave_allowance,
                              annual_leave_allowance_hour=salary_template.annual_leave_allowance_hour,
                              annual_leave_allowance_day=salary_template.annual_leave_allowance_day,
                              hire_year=salary_template.hire_year,
                              job_allowance=branch.allowance_policies.job_allowance,
                              meal_allowance=branch.allowance_policies.meal_allowance, 
                              holiday_allowance=(
                                  branch.allowance_policies.doctor_holiday_work_pay 
                                  if salary_template.part.is_doctor 
                                  else branch.allowance_policies.common_holiday_work_pay)
                            ) for salary_template in salary_templates]

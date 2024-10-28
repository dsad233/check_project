from fastapi import APIRouter

from app.api.routes.auth import auth
from app.api.routes.branches import branches
from app.api.routes.commutes import commutes
from app.api.routes.labor_management import part_timer
from app.api.routes.leave_category import leave_category
from app.api.routes.leave_histories import leave_histories
from app.api.routes.closed_days import closed_days
from app.api.routes.overtimes import overtimes
from app.api.routes.overtime_manager import overtime_manager
from app.api.routes.parts import parts
from app.api.routes.parts_policy import parts_policy
from app.api.routes.salary_bracket import salary_bracket
from app.api.routes.users import users, user_management
from app.api.routes.users.user_management_contract import user_management_contract
from app.api.routes.users.user_management_document import user_management_document
from app.api.routes.users.user_management_work_contract import user_management_work_contract
from app.api.routes.work_policies import work_policies
from app.api.routes.hour_wage_template import hour_wage_template
from app.api.routes.attendance import attendance
from app.api.routes.commutes_manager import commutes_manager
from app.api.routes.leave_policies import leave_policies
from app.api.routes.menu_management import menu_management
from app.api.routes.minimum_wage_policies import minimum_wage_policies
from app.api.routes.salary_template import salary_template
from app.api.routes.salary_policies import salary_policies
from app.api.routes.modusign import document, template

app = APIRouter()

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(commutes.router, prefix="/commutes", tags=["Commutes"])
app.include_router(overtimes.router, prefix="/overtimes", tags=["Overtimes"])
app.include_router(overtime_manager.router, prefix="/branches", tags=["Overtimes_Manager"])
app.include_router(closed_days.router, prefix="/branches", tags=["Closed Days"])

app.include_router(branches.router, prefix="/branches", tags=["Branches"])
app.include_router(parts.router, prefix="/branches/{branch_id}/parts", tags=["Parts"])
app.include_router(leave_category.router, prefix="/branches/{branch_id}/leave-categories", tags=["leave_categories"])
app.include_router(leave_histories.router, prefix='/leave-histories', tags=['leave_Histories'])
app.include_router(work_policies.router, prefix='/branches/{branch_id}/work-policies', tags=['work_policies'])
app.include_router(hour_wage_template.router, prefix='/branches/{branch_id}/hour-wage-templates', tags=['hour_wage_templates'])
app.include_router(parts_policy.router, prefix="/branches/{branch_id}/parts-policies", tags=["Parts_policies"])

app.include_router(salary_bracket.router, prefix='/salary-bracket', tags=['Salary Bracket'])
app.include_router(user_management_document.router, prefix='/user-management/document', tags=['User_Management_Document'])
app.include_router(user_management_contract.router, prefix='/user-management/contract', tags=['User_Management_Contract'])
app.include_router(user_management_work_contract.router, prefix='/user-management/work-contract', tags=['User_Management_Work_Contract'])
app.include_router(user_management.router, prefix='/user-management', tags=['User_Management'])

app.include_router(attendance.router, prefix="/branches", tags=["Attendance"])
app.include_router(commutes_manager.router, prefix="/branches", tags=["commutes_manager"])
app.include_router(part_timer.router, prefix="/labor-management", tags=["Part_timer"])

app.include_router(leave_policies.router, prefix='/branches/{branch_id}/leave-policies', tags=['Leave_Policies'])
app.include_router(menu_management.router, prefix='/menu-management', tags=['Menu_Management'])
app.include_router(minimum_wage_policies.router, prefix='/minimum-wage-policies', tags=['Minimum_Wage_Policies'])
app.include_router(salary_template.router, prefix='/branches/{branch_id}/salary-templates', tags=['Salary_Templates'])
app.include_router(salary_policies.router, prefix='/branches/{branch_id}/salary-policies', tags=['Salary_Policies'])
app.include_router(document.router, prefix='/modusign-document', tags=['Modusign_Document'])
app.include_router(template.router, prefix='/modusign-template', tags=['Modusign_Template'])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
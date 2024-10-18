from fastapi import APIRouter

from app.api.routes.auth import auth
from app.api.routes.branches import branches
from app.api.routes.commutes import commutes
from app.api.routes.leave_category import leave_category
from app.api.routes.leave_histories import leave_histories
from app.api.routes.overtime_policies import overtime_policies
from app.api.routes.closed_days import closed_days
from app.api.routes.overtimes import overtimes
from app.api.routes.parts import parts
from app.api.routes.parts_policy import parts_policy
from app.api.routes.salary_bracket import salary_bracket
from app.api.routes.users import users
from app.api.routes.work_policies import work_policies
from app.api.routes.users.user_management import user_management
from app.api.routes.hour_wage_template import hour_wage_template

app = APIRouter()

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(commutes.router, prefix="/commutes", tags=["Commutes"])
app.include_router(overtimes.router, prefix="/overtimes", tags=["Overtimes"])
app.include_router(closed_days.router, prefix="/branches", tags=["Closed Days"])

app.include_router(branches.router, prefix="/branches", tags=["Branches"])
# app.include_router(overtime_policies.router, prefix="/branches", tags=["Overtime_policies"])
app.include_router(parts.router, prefix="/branches/{branch_id}/parts", tags=["Parts"])
app.include_router(leave_category.router, prefix="/branches/{branch_id}/leave-categories", tags=["Leave Categories"])
app.include_router(leave_histories.router, prefix='/branches/{branch_id}/leaves', tags=['Leave Histories'])
app.include_router(work_policies.router, prefix='/branches/{branch_id}/work-policies', tags=['Work_policies'])
app.include_router(hour_wage_template.router, prefix='/branches/{branch_id}/hour-wage-templates', tags=['Hour_wage_templates'])
app.include_router(parts_policy.router, prefix="/branches/{branch_id}/parts-policies", tags=["Parts_policies"])

app.include_router(salary_bracket.router, prefix='/salary-bracket', tags=['Salary Bracket'])
app.include_router(user_management.router, prefix='/user-management', tags=['User_Management'])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
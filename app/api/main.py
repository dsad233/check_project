from fastapi import APIRouter

from app.api.routes.auth import auth
from app.api.routes.branches import branches
from app.api.routes.commutes import commutes
from app.api.routes.human_record_category import human_record_category
from app.api.routes.leave_category import leave_category

# from app.api.routes.annual_leaves import annual_leaves
from app.api.routes.overtime_policies import overtime_policies
from app.api.routes.closed_days import closed_days
from app.api.routes.parts import parts
from app.api.routes.parts_policy import parts_policy
from app.api.routes.salary_bracket import salary_bracket
from app.api.routes.users import users

app = APIRouter()

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(parts.router, prefix="/branches/{branch_id}/parts", tags=["Parts"])
app.include_router(
    parts_policy.router,
    prefix="/branches/{branch_id}/parts_policies",
    tags=["Parts_policies"],
)
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(commutes.router, prefix="/commutes", tags=["Commutes"])
app.include_router(closed_days.router, prefix="/closed-days", tags=["Closed Days"])
app.include_router(
    overtime_policies.router, prefix="/branches", tags=["Overtime_policies"]
)
app.include_router(branches.router, prefix="/branches", tags=["Branches"])
app.include_router(leave_category.router, prefix="/branches/{branch_id}/leave-categories", tags=["Leave Categories"])
app.include_router(salary_bracket.router, prefix='/salary-bracket', tags=['Salary Bracket'])
app.include_router(human_record_category.router, prefix='/branches/{branch_id}/hr-categories', tags=['HR Categories'])

@app.get("/health")
def health_check():
    return {"status": "healthy"}


# app.include_router(annual_leaves.router, prefix='/annual-leaves', tags=['Annual Leaves'])
# app.include_router(overtimes.router, prefix='/overtime', tags=['Overtime'])

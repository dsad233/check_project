from fastapi import APIRouter

from app.api.routes.auth import auth
from app.api.routes.branch_policies import branch_policies
from app.api.routes.parts import parts
from app.api.routes.users import users

# from app.api.routes.annual_leaves import annual_leaves
# from app.api.routes.overtimes import overtimes

app = APIRouter()

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(parts.router, prefix="/parts", tags=["Parts"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(
    branch_policies.router, prefix="/branch_policies", tags=["Branch_policies"]
)
# app.include_router(annual_leaves.router, prefix='/annual-leaves', tags=['Annual Leaves'])
# app.include_router(overtimes.router, prefix='/overtime', tags=['Overtime'])

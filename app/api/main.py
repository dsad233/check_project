from fastapi import APIRouter
from app.api.routes.auth import auth
from app.api.routes.overtimes import overtimes

app = APIRouter()

app.include_router(auth.router, prefix='/auth', tags=['Auth'])
app.include_router(overtimes.router, prefix='/overtime', tags=['Overtime'])
from fastapi import APIRouter
from app.api.routes.auth import auth

app = APIRouter()

app.include_router(auth.router, prefix='/auth', tags=['Auth'])
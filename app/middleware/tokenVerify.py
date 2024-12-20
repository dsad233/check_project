from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.database import async_session, get_db
from app.exceptions.exceptions import ForbiddenError
from app.middleware.jwt.jwtService import JWTDecoder, JWTService
from app.models.users.users_model import Users
from app.middleware.permission import UserPermission
from app.enums.users import Role

# users = async_session()

auth_header = APIKeyHeader(name="Authorization-Swagger", auto_error=False)

async def validate_token(
        req: Request,
        auth: str = Security(auth_header),
        users: AsyncSession = Depends(get_db)
        ):
    
    try:
        
        # 스웨거를 위한 처리
        if auth:
            header = f"Bearer {auth}"
        else:
            # 다른 클라이언트를 위한 처리
            header = req.headers.get("Authorization")
        
        if not header:
            raise HTTPException(status_code=401, detail="로그인을 진행해주세요.")
        
        parts = header.split()
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="잘못된 인증 헤더 형식입니다.")
        
        token_type, token = parts

        if token_type.lower() != "bearer":
            raise HTTPException(status_code=400, detail="토큰 타입이 일치하지 않습니다.")
        if not token:
            raise HTTPException(status_code=400, detail="토큰이 존재하지 않습니다.")
        
        jwtService = JWTService(None, JWTDecoder())
        jwtVerify = jwtService.check_token_expired(token)

        if jwtVerify is None:
            raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
        
        user_id = jwtVerify.get("id")
        # stmt = select(Users).where((Users.id == user_id) & (Users.deleted_yn == "N") & (Users.role != "퇴사자"))
        stmt = (
            select(Users)
            .options(
                joinedload(Users.branch),  # 1:1 관계는 joinedload
                selectinload(Users.parts)  # 1:N 관계는 selectinload
            )
            .where(
                (Users.id == user_id) &
                (Users.deleted_yn == "N") &
                ~Users.role.in_([Role.RESIGNED, Role.ON_LEAVE]) # 퇴사자, 휴직자 접근 제한
            )
        )
        result = await users.execute(stmt)
        find_user = result.scalar_one_or_none()

        if find_user is None:
            raise HTTPException(
                status_code=401,  # 401로 변경
                detail="접근 권한이 없습니다. (퇴사자/휴직자이거나 존재하지 않는 사용자입니다)"
            )

        req.state.user_id = user_id
        req.state.user = find_user

    except HTTPException as http_err:
        print(f"HTTP 에러가 발생하였습니다: {http_err.detail}")
        raise
    except Exception as err:
       print(f"예상치 못한 에러가 발생하였습니다: {str(err)}")
       import traceback
       traceback.print_exc()
       raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

# 현재 사용자 ID를 가져오는 함수
async def get_current_user_id(req: Request):
    return req.state.user_id


# 현재 사용자를 가져오는 함수
async def get_current_user(req: Request):
    return req.state.user

async def check_branch_access(
    req: Request,
    branch_id: int,  # path parameter를 직접 받음
    user: Users = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    if user.role != Role.MSO.value and user.branch_id != branch_id:
        raise ForbiddenError(detail="해당 지점에 대한 접근 권한이 없습니다.")

    return user

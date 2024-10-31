from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from app.core.database import async_session
from app.exceptions.exceptions import UnauthorizedError
from app.middleware.jwt.jwtService import JWTDecoder, JWTService
from app.models.users.users_model import Users
from app.enums.users import Role


class TokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        async with async_session() as session:
                path = request.url.path

                # OPTIONS 요청 처리
                if request.method == "OPTIONS":
                    return await call_next(request)

                # 인증이 필요없는 경로들
                public_paths = [
                    "/callback",
                    "/auth/login",
                    "/healthcheck",
                    "/docs",
                    "/openapi.json",
                    "/redoc",
                    "/favicon.ico"
                ]

                # public paths 체크
                if any(path.startswith(p) for p in public_paths):
                    return await call_next(request)

                # 헤더 체크
                auth = request.headers.get("Authorization-Swagger")
                header = f"Bearer {auth}" if auth else request.headers.get("Authorization")

                if not header:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "로그인을 진행해주세요."}
                    )

                parts = header.split()
                # 400 Bad Request - 잘못된 요청 형식
                if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "잘못된 인증 헤더 형식입니다."}
                    )

                token_type, token = parts

                # JWT 검증
                jwtService = JWTService(None, JWTDecoder())
                jwtVerify = jwtService.check_token_expired(token)

                # 401 Unauthorized - 토큰 만료
                if jwtVerify is None:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "토큰이 만료되었습니다."}
                    )

                # 사용자 조회
                user_id = jwtVerify.get("id")
                stmt = (
                    select(Users)
                    .options(
                        joinedload(Users.branch),
                        selectinload(Users.parts)
                    )
                    .where(
                        (Users.id == user_id) &
                        (Users.deleted_yn == "N") &
                        ~Users.role.in_([Role.RESIGNED, Role.ON_LEAVE])  # 퇴사자, 휴직자 접근 제한
                    )
                )
                result = await session.execute(stmt) #DB 작업 수행
                find_user = result.scalar_one_or_none()

                # 401 Unauthorized - 사용자 없음/권한 없음
                if find_user is None:
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "접근 권한이 없습니다. (퇴사자/휴직자이거나 존재하지 않는 사용자입니다)"}
                    )

                # 요청 객체에 사용자 정보 추가
                request.state.user_id = user_id
                request.state.user = find_user

                response = await call_next(request)
                return response

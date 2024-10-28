from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from app.core.database import async_session
from app.middleware.jwt.jwtService import JWTDecoder, JWTService
from app.models.users.users_model import Users


class TokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.users = async_session()

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # OPTIONS 요청 처리
        if request.method == "OPTIONS":
            return await call_next(request)

        # 인증이 필요없는 경로들
        public_paths = [
            "/auth/login",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        ]

        # public paths 체크
        if any(path.startswith(p) for p in public_paths):
            return await call_next(request)

        try:
            # 헤더 체크
            auth = request.headers.get("Authorization-Swagger")
            header = f"Bearer {auth}" if auth else request.headers.get("Authorization")

            if not header:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "로그인을 진행해주세요."}
                )

            parts = header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "잘못된 인증 헤더 형식입니다."}
                )

            token_type, token = parts

            # JWT 검증
            jwtService = JWTService(None, JWTDecoder())
            jwtVerify = jwtService.check_token_expired(token)

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
                    (Users.role != "퇴사자")
                )
            )

            try:
                result = await self.users.execute(stmt)
                find_user = result.scalar_one_or_none()
            except Exception as db_err:
                print(f"데이터베이스 조회 중 에러 발생: {str(db_err)}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": "사용자 정보 조회 중 오류가 발생했습니다."}
                )

            if find_user is None:
                return JSONResponse(
                    status_code=404,
                    content={"detail": "유저가 존재하지 않습니다."}
                )

            # 요청 객체에 사용자 정보 추가
            request.state.user_id = user_id
            request.state.user = find_user

            response = await call_next(request)
            return response

        except Exception as err:
            print(f"토큰 검증 중 에러 발생: {str(err)}")
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=401,
                content={"detail": "인증에 실패했습니다."}
            )
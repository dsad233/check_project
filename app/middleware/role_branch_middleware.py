from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.enums.users import Role


class RoleBranchMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

        # public paths는 TokenMiddleware와 동일하게 유지
        self.PUBLIC_PATHS = [
            "/auth/login",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        ]

        # 일반 사원 접근 가능 경로
        self.EMPLOYEE_PATHS = {
            "/users/me/"  # /users/me/* 모든 하위 경로 포함

        }

        # 관리자 이상(파트 관리자 이상) 접근 가능 경로
        self.ADMIN_PATHS = {
            "/user-management/",
            "/branches/",
            "/menu-management/"
        }

        # # 통합 관리자 이상 접근 가능 경로
        # self.INTEGRATED_ADMIN = {
        #     "/"
        # }

        # MSO 이상 접근용
        self.MSO_PATHS = {
            # "/modusign-template/"
        }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # OPTIONS 요청 처리
        if request.method == "OPTIONS":
            return await call_next(request)

        # public paths 체크
        if any(path.startswith(p) for p in self.PUBLIC_PATHS):
            return await call_next(request)

        # 로그인 체크
        if not hasattr(request.state, "user") or request.state.user is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "로그인이 필요합니다."}
            )

        user = request.state.user

        # MSO 전용 경로 체크
        if any(path.startswith(p) for p in self.MSO_PATHS):
            if user.role != Role.MSO:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "MSO 권한이 필요합니다."}
                )

        # 관리자 경로 체크
        if any(path.startswith(p) for p in self.ADMIN_PATHS):
            if user.role not in [Role.MSO, Role.SUPER_ADMIN, Role.ADMIN]:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "관리자 이상의 권한이 필요합니다."}
                )

        # 그 외는 모든 로그인 사용자 접근 가능 - TODO) 개발 모드 / 배포 모드일 경우에는 에러 처리 필요
        return await call_next(request)
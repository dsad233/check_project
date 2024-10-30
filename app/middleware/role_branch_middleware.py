from typing import Optional
import re
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.enums.users import Role
from app.core.permissions.auth_utils import RoleAuthority


class RoleBranchMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

        # 정규식 패턴: /branches/숫자로 시작하는 모든 경로 체크
        self.BRANCH_ID_PATTERN = re.compile(r"^/branches/(\d+)(?:/.*)?$")

        # public paths는 TokenMiddleware와 동일하게 유지
        self.PUBLIC_PATHS = [
            "/auth/login",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        ]

        # 일반 사원 이상 접근 가능 경로
        self.EMPLOYEE_LEVEL_PATHS = {
            "/users/",
            "/commutes/clock-in",
            "/commutes/clock-out",
            "/overtimes",
            "/overtimes/manager"
            "/leave-categories",
            "/leave-histories",
            "/leave-histories/list"
            "/user-management",
            "/user-management/me"
        }

        # 관리자 이상 접근 가능 경로
        self.ADMIN_LEVEL_PATHS = {
            "/branches",
            "/menu-management",
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


        user = request.state.user

        # 퇴사자/휴직자 접근 제한
        if user.role in [Role.RESIGNED, Role.ON_LEAVE]:
            return JSONResponse(
                status_code=403,
                content={"detail": "접근 권한이 없습니다. (퇴사자/휴직자)"}
            )

        # /branches/{branch_id}/* 패턴 체크
        branch_match = self.BRANCH_ID_PATTERN.match(path)
        if branch_match:
            branch_id = int(branch_match.group(1))
            print(branch_id, "::::", user.role)
            # MSO가 아니고 본인 지점이 아닌 경우
            if user.role != Role.MSO and user.branch_id != branch_id:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "해당 지점에 대한 접근 권한이 없습니다. 본인 소속 지점만 접근할 수 있습니다."}
                )


        # MSO 전용 경로 체크
        if any(path.startswith(p) for p in self.MSO_PATHS):
            if user.role != Role.MSO:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "MSO 권한이 필요합니다."}
                )

        # 관리자 레벨 경로 체크
        if any(path.startswith(p) for p in self.ADMIN_LEVEL_PATHS):
            if not RoleAuthority.check_role_level(user.role, Role.ADMIN):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "관리자 이상의 권한이 필요합니다."}
                )

        # 일반 사원 레벨 경로 체크
        if any(path.startswith(p) for p in self.EMPLOYEE_LEVEL_PATHS):
            if not RoleAuthority.check_role_level(user.role, Role.EMPLOYEE):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "접근 권한이 없습니다."}
                )

        # 그 외 TODO) 개발 모드 / 배포 모드일 경우에는 에러 처리 필요
        return await call_next(request)
from typing import Optional, Dict, Pattern, NamedTuple
import re
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.enums.users import Role
from app.core.permissions.auth_utils import RoleAuthority


class RouteConfig(NamedTuple):
    """라우트 설정을 위한 데이터 클래스"""
    required_role: Role #해당 라우트에 접근하기 위해 필요한 최소 권한
    check_branch: bool = False #지점 접근 권한 검사 여부


class RoleBranchMiddleware(BaseHTTPMiddleware):
    """역할 기반 접근 제어 및 지점 접근 권한을 관리하는 미들웨어
        1. URL prefix에 따른 역할 기반 접근 제어
        2. 지점 관련 엔드포인트에 대한 접근 권한 검사
        3. MSO 역할에 대한 특별 권한 처리
        """

    def __init__(self, app):
        super().__init__(app)

        # 라우트 설정
        # - admin: 관리자 권한(파트/통합/최고/mso) 필요, 지점 체크 필요
        # - employee: 사원 권한 필요, 지점 체크 필요
        # - mso: MSO 권한 필요, 지점 체크 불필요 (모든 지점 접근 가능)
        self.ROUTE_CONFIG = {
            "admin": RouteConfig(Role.ADMIN, check_branch=True),
            "employee": RouteConfig(Role.EMPLOYEE, check_branch=True),
            "mso": RouteConfig(Role.MSO, check_branch=False)
        }

        # 지점 접근 패턴을 위한 단일 정규표현식
        # Format: /{prefix}/branches/{branch_id}/...
        # Example: /admin/branches/123/users
        self.BRANCH_PATTERN = re.compile(r"^/(?P<prefix>\w+)/branches/(?P<branch_id>\d+)(?:/.*)?$")

    def _check_authorization(self, path: str, user_role: Role, user_branch_id: int) -> Optional[JSONResponse]:
        """권한 검사"""
        # 1. 경로에서 prefix 추출
        # / admin / ... -> admin
        # /employee/... -> employee
        prefix = path.split('/')[1] if len(path.split('/')) > 1 else None

        # 등록된 prefix가 아니면 권한 검사 없이 통과 (public 라우트)
        if not prefix or prefix not in self.ROUTE_CONFIG:
            return None

        config = self.ROUTE_CONFIG[prefix]

        # 2. 사용자의 역할이 요구되는 최소 권한 레벨을 만족하는지 검사
        if not RoleAuthority.check_role_level(user_role, config.required_role):
            return JSONResponse(
                status_code=401,
                content={
                    "detail": f"{config.required_role.value} 이상의 권한이 필요합니다. (현재: {user_role})"
                }
            )

        # 3. 지점 접근 권한 검사 (필요한 경우만)
        # - check_branch가 True인 경우에만 수행
        # - MSO 역할은 모든 지점에 접근 가능
        # - 그 외 역할은 자신이 속한 지점만 접근 가능
        if config.check_branch:
            match = self.BRANCH_PATTERN.match(path)
            if match and match.group('prefix') == prefix:
                branch_id = int(match.group('branch_id'))
                if user_role != Role.MSO and user_branch_id != branch_id:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "detail": f"본인 소속 지점의 데이터만 접근할 수 있습니다. (현재 역할: {user_role}, 속한 지점: {user_branch_id})"
                        }
                    )

        return None

    async def dispatch(self, request: Request, call_next):
        """모든 HTTP 요청에 대한 권한 검사를 수행하는 디스패처"""
        # CORS preflight 요청 처리
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path

        # prefix 확인 (public path 체크)
        prefix = path.split('/')[1] if len(path.split('/')) > 1 else None
        if not prefix or prefix not in self.ROUTE_CONFIG:
            # public 라우트는 권한 검사 없이 통과
            return await call_next(request)

        # 인증이 필요한 경로에서만 user 정보 확인
        try:
            user = request.state.user
        except AttributeError:
            return JSONResponse(
                status_code=401,
                content={"detail": "인증이 필요합니다."}
            )

        # 통합된 권한 검사 수행
        auth_result = self._check_authorization(path, user.role, user.branch_id)
        if auth_result:
            return auth_result

        return await call_next(request)
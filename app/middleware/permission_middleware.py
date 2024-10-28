from fastapi import Request, HTTPException
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.enums.users import Role


class PermissionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path

        # 권한 체크가 필요없는 경로들
        public_paths = [
            "/auth/login",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        ]

        # public paths인 경우만 바로 통과
        if any(path.startswith(p) for p in public_paths):
            return await call_next(request)

        try:
            user = request.state.user
            if not user:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "인증되지 않은 사용자입니다."}
                )

            # 기본 권한 체크
            await self._check_basic_permission(user, request)

            return await call_next(request)
        except AttributeError:
            # request.state.user가 없는 경우
            raise HTTPException(status_code=401, detail="인증이 필요합니다.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def _check_basic_permission(self, user, request: Request):
        """공통적인 기본 권한 체크 로직"""
        # MSO는 모든 권한 허용
        if user.role.strip() == Role.MSO:
            return True

        # URL에서 branch_id 추출
        branch_id = self._get_path_param(request.path_params, 'branch_id')
        if branch_id and user.branch_id != int(branch_id):
            if user.role.strip() not in [Role.SUPER_ADMIN, Role.INTEGRATED_ADMIN]:
                raise HTTPException(status_code=403, detail="해당 지점에 접근할 권한이 없습니다.")

    def _get_path_param(self, path_params: dict, param_name: str) -> Optional[str]:
        """URL 파라미터 추출 헬퍼 메서드"""
        return path_params.get(param_name)
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.enums.users import Role


class PermissionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.public_paths = [
            "/auth/login",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        ]

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        if any(path.startswith(p) for p in self.public_paths):
            return await call_next(request)

        try:
            # validate_token dependency가 실행되기 전이므로
            # 여기서는 user가 없을 수 있음 - 그냥 통과시킴
            if not hasattr(request.state, 'user'):
                return await call_next(request)

            user = request.state.user

            # MSO는 모든 권한 허용
            if user.role.strip() == Role.MSO:
                return await call_next(request)

            # 지점 접근 권한 체크
            branch_id = self._get_path_param(request.path_params, 'branch_id')
            if branch_id and user.branch_id != int(branch_id):
                if user.role.strip() not in [Role.SUPER_ADMIN, Role.INTEGRATED_ADMIN]:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "해당 지점에 접근할 권한이 없습니다."}
                    )

            return await call_next(request)

        except Exception as e:
            print(f"Permission Middleware Error: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"detail": "권한이 없습니다."}
            )

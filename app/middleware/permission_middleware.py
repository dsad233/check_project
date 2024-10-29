from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.enums.users import Role
from app.exceptions.exceptions import ForbiddenError


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
        try:  # try 블록 추가
            if request.method == "OPTIONS":
                return await call_next(request)

            path = request.url.path
            if any(path.startswith(p) for p in self.public_paths):
                return await call_next(request)

            path_parts = request.url.path.split('/')
            branch_id = None

            for i, part in enumerate(path_parts):
                if part == "branches" and i + 1 < len(path_parts):
                    try:
                        branch_id = int(path_parts[i + 1])
                    except ValueError:
                        continue

            if branch_id is not None:
                user = getattr(request.state, 'user', None)
                if user and user.role != Role.MSO and user.branch_id != branch_id:
                    raise ForbiddenError(detail="해당 지점에 대한 권한이 없습니다.")

            # 권한 체크가 끝난 후 실제 요청 처리
            response = await call_next(request)
            return response

        except ForbiddenError as fe:
            raise fe  # FastAPI의 예외 처리기로 전달
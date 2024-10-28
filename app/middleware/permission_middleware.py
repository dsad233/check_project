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
            # URL에서 branch_id 추출 (branches 다음에 오는 숫자만 추출)
            path_parts = request.url.path.split('/')
            branch_id = None

            for i, part in enumerate(path_parts):
                if part == "branches" and i + 1 < len(path_parts):
                    try:
                        branch_id = int(path_parts[i + 1])
                        break
                    except ValueError:
                        continue

            # 지점 접근 권한 체크만 수행
            if branch_id is not None:
                response = await call_next(request)
                if response.status_code == 200:
                    user = getattr(request.state, 'user', None)
                    if user and user.role != Role.MSO and user.branch_id != branch_id:
                        return JSONResponse(
                            status_code=401,
                            content={"detail": "해당 지점에 접근할 권한이 없습니다."}
                        )
                return response

            return await call_next(request)

        except Exception as e:
            print(f"Permission Middleware Error: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"detail": "권한이 없습니다."}
            )

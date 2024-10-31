from typing import Callable, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.database import startup_event
from app.exceptions.exceptions import add_exception_handlers
from app.api import main
from app.api.routes.auth import auth
from contextlib import asynccontextmanager
from app.core.log_config import get_logger
from app.middleware.token_middleware import TokenMiddleware
from app.middleware.role_branch_middleware import RoleBranchMiddleware
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield


# FastAPI 앱 생성 시 Swagger UI 기본 설정 추가
app = FastAPI(
    lifespan=lifespan,
    title="Check API 명세서",
    description="Check API Documentation",
    version="1.0.0",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1 ,  # 모델 섹션 접기
        "docExpansion": "none",          # 모든 엔드포인트 접기
        "filter": True,                   # 검색 필터 활성화
        "persistAuthorization": False      # 인증 정보 유지
    }
)

# OpenAPI 커스텀 설정 추가
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Check API 명세서",
        version="1.0.0",
        description="Check API Documentation",
        routes=app.routes,
    )

    # 단일 보안 스키마
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**"
        }
    }
    # 태그 및 보안 요구사항 설정
    tags = []
    if "paths" in openapi_schema:
        for path in openapi_schema["paths"]:
            # 보안 설정
            if not any(path.startswith(public_path) for public_path in settings.PUBLIC_PATHS):
                for method in openapi_schema["paths"][path].keys():
                    if method.lower() != "options":
                        openapi_schema["paths"][path][method]["security"] = [{"Bearer": []}]

            # 태그 수집
            for method in openapi_schema["paths"][path].values():
                if "tags" in method and method["tags"]:
                    tags.extend(method["tags"])

    # 태그 설정 (중복 제거 및 기본 접힘 상태 설정)
    unique_tags = sorted(set(tags))  # 알파벳 순 정렬
    openapi_schema["tags"] = [
        {
            "name": tag,
            "description": f"{tag} 관련 API",
            "x-display-name": tag,
            "x-collapsed": True
        }
        for tag in unique_tags
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# OpenAPI 커스텀 설정 적용
app.openapi = custom_openapi


origins = [
    "https://workswave-frontend-one.vercel.app",
    "https://develop-check.mementoai.io",
    "http://localhost:5173",
    "http://52.78.246.46"
]

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization", "Authorization_Swagger"],
)

app.add_middleware(RoleBranchMiddleware)  #type: ignore #RoleBranchMiddleware가 user 정보를 사용

app.add_middleware(TokenMiddleware)     #type: ignore #TokenMiddleware가 먼저 실행되어 user 정보를 설정

# Register exception handlers
add_exception_handlers(app)
app.include_router(main.app)
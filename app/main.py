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


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "https://workswave-frontend-one.vercel.app",
    "https://develop-check.mementoai.io",
    "http://localhost:5173",
    "http://52.78.246.46"
]

# Register exception handlers
add_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization", "Authorization_Swagger"],
)


# Add token middleware
app.add_middleware(TokenMiddleware) #type: ignore

# app.include_router(auth.router, prefix="/api")


# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="Your API",
#         version="1.0.0",
#         description="Your API description",
#         routes=app.routes,
#     )
#     openapi_schema["components"]["securitySchemes"] = {
#         "Authorization_Swagger": {
#             "type": "apiKey",
#             "in": "header",
#             "name": "Authorization_Swagger",
#         }
#     }
#     openapi_schema["security"] = [{"Authorization_Swagger": []}]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi
app.include_router(main.app)
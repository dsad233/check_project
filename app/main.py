from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.database import startup_event
from app.exceptions.exceptions import add_exception_handlers
from app.api import main
from app.api.routes.auth import auth
from contextlib import asynccontextmanager
from app.core.log_config import get_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "https://workswave-frontend-one.vercel.app",
    "http://localhost:5173",
    "http://52.78.246.46"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization", "Authorization_Swagger"],
)
# Register exception handlers
add_exception_handlers(app)

app.include_router(auth.router, prefix="/api")


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
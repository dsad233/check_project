from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api import main
from app.api.routes.auth import auth

app = FastAPI()

origins = [
    "https://workswave-frontend.vercel.app",
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

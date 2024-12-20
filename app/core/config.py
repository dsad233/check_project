import os
from typing import Union
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
import base64

# API 공개 경로 정의
PUBLIC_PATHS = [
    "/callback",
    "/auth/login",
    "/healthcheck",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/favicon.ico",
    "/monitor",
    "/metrics/connections",
    "/metrics/max-connections",
    "/metrics/connection-history"
]


class BaseAppSettings(BaseSettings):
    # PUBLIC_PATHS를 설정 클래스의 속성으로 추가
    PUBLIC_PATHS: list[str] = PUBLIC_PATHS

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    MODUSIGN_API_KEY: str
    MODUSIGN_USER_EMAIL: str  
    MODUSIGN_WEBHOOK_URL: str
    SLACK_HOOK : str
    USERNAME : str
    CHANNEL : str
    API_URL : str 
    
    
    @property
    def MODUSIGN_HEADERS(self) -> dict:
        if not self.MODUSIGN_API_KEY or not self.MODUSIGN_USER_EMAIL:
            raise ValueError("MODUSIGN_API_KEY and MODUSIGN_USER_EMAIL are required")
            
        auth_string = f"{self.MODUSIGN_USER_EMAIL}:{self.MODUSIGN_API_KEY}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_auth}"
        }

    model_config = ConfigDict(
        env_file=(".env"),
        case_sensitive=False,  # 환경 변수 대소문자 구분 안함
        extra="ignore",        # 추가 필드 무시
        validate_assignment=True  # 할당 시에도 유효성 검사
    )



class DevSettings(BaseAppSettings):
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_DATABASE: str

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    model_config = ConfigDict(
        env_file=(".env", ".env.dev"),
        case_sensitive=False,  # 환경 변수 대소문자 구분 안함
        extra="ignore",        # 추가 필드 무시
        validate_assignment=True  # 할당 시에도 유효성 검사
    )

class ProdSettings(BaseAppSettings):
    RDS_USER: str
    RDS_PASSWORD: str
    RDS_HOST: str
    RDS_PORT: int
    RDS_DATABASE: str

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.RDS_USER}:{self.RDS_PASSWORD}@{self.RDS_HOST}:{self.RDS_PORT}/{self.RDS_DATABASE}"

    model_config = ConfigDict(
        env_file=(".env", ".env.prod"),
        case_sensitive=False,  # 환경 변수 대소문자 구분 안함
        extra="ignore",        # 추가 필드 무시
        validate_assignment=True  # 할당 시에도 유효성 검사
    )


class LocalSettings(BaseAppSettings):
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_DATABASE: str
    MYSQL_ROOT_PASSWORD: str

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    model_config = ConfigDict(
        env_file=(".env", ".env.local"),
        case_sensitive=False,  # 환경 변수 대소문자 구분 안함
        extra="ignore",        # 추가 필드 무시
        validate_assignment=True  # 할당 시에도 유효성 검사
    )


def load_settings() -> Union[DevSettings, ProdSettings, LocalSettings]:
    mode = os.getenv("MODE", "dev")

    if mode == "dev":
        return DevSettings()
    elif mode == "prod":
        return ProdSettings()
    elif mode == "local":
        return LocalSettings()
    else:
        raise ValueError(f"Unsupported environment: {mode}")
    


settings = load_settings()
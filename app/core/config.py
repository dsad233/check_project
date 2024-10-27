import os
from typing import Union
from pydantic_settings import BaseSettings
from pydantic import Field

class BaseAppSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    # MODUSIGN_API_KEY: str = Field(..., env="MODUSIGN_API_KEY")
    # MODUSIGN_WEBHOOK_URL: str = Field(..., env="MODUSIGN_WEBHOOK_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False

class DevSettings(BaseAppSettings):
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_DATABASE: str
    MYSQL_ROOT_PASSWORD: str

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    class Config:
        env_file = (".env", ".env.dev")

class ProdSettings(BaseAppSettings):
    RDS_USER: str
    RDS_PASSWORD: str
    RDS_HOST: str
    RDS_PORT: int
    RDS_DATABASE: str

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.RDS_USER}:{self.RDS_PASSWORD}@{self.RDS_HOST}:{self.RDS_PORT}/{self.RDS_DATABASE}"

    class Config:
        env_file = (".env", ".env.prod")

def load_settings() -> Union[DevSettings, ProdSettings]:
    mode = os.getenv("MODE", "prod")

    if mode == "dev":
        return DevSettings()
    elif mode == "prod":
        return ProdSettings()
    else:
        raise ValueError(f"Unsupported environment: {mode}")

settings = load_settings()
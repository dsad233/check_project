from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET_KEY : str
    JWT_ALGORITHM : str

    DATABASE_URL : str
    class Config:
        env_file = ".env" 

settings = Settings()
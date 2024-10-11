import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    JWT_SECRET_KEY : str = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM : str = os.getenv('JWT_ALGORITHM')

    DATABASE_URL : str = os.getenv('DATABASE_URL')

settings = Settings()

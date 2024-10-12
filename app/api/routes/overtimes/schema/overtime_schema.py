from pydantic_settings import BaseSettings
from datetime import datetime

class OverTimeCreate(BaseSettings):
    application_date : datetime
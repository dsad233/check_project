from datetime import datetime

from pydantic_settings import BaseSettings


class OverTimeCreate(BaseSettings):
    application_date: datetime

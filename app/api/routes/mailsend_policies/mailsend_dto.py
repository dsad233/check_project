from pydantic_settings import BaseSettings
from pydantic import Field


class MailSend(BaseSettings):
    title : str = Field(None, description="메일 전송 제목")
    context : str = Field(None, description= "메일 전송 내용")
from pydantic_settings import BaseSettings
from sqlalchemy import Column, Integer, String
from app.core.database import Base
from pydantic import Field
class MailSend_Model(Base):
    __table__ = "mail_send"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False)

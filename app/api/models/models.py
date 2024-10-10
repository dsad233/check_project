from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.api.core.database import Base

class Users(Base):
   __tablename__ = "users"

   id = Column(Integer, autoincrement=True, primary_key=True)
   password = Column(String(length=255), nullable=False)
   name = Column(String(length=10), nullable=False, unique=True)
   isOpen = Column(Boolean, default=True)
   image = Column(String(length=255), nullable=True)
   createdAt = Column(DateTime, default= datetime.now)
   updatedAt = Column(DateTime, default= datetime.now, onupdate=datetime.now)
   deletedAt = Column(DateTime, nullable= True)

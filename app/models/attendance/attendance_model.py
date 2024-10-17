from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, String
from app.core.database import Base


class Attendance(Base):
    __tablename__ = "attendance"


    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    part_id = Column(Integer, ForeignKey('parts.id'), nullable=False)
    part_name = Column(String(255), nullable=False)
    name = Column(String(10),nullable=False)
    gender = Column(String(5), nullable= False)

    



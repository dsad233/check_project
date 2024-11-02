# ConnectionLogs 모델 수정
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.types import TypeDecorator
from app.core.database import Base
import pytz

class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                value = pytz.timezone('Asia/Seoul').localize(value)
            return value.astimezone(pytz.UTC)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return pytz.UTC.localize(value).astimezone(pytz.timezone('Asia/Seoul'))
        return value

class ConnectionLogs(Base):
    __tablename__ = "connection_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    connection_count = Column(Integer, nullable=False)
    created_at = Column(TZDateTime, nullable=False)
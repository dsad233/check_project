from pydantic import BaseModel
from datetime import datetime

class PaginationDto(BaseModel):
    total_record: int # 총 레코드 수
    record_size: int = 10 # 한 페이지당 레코드 수
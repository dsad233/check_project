from pydantic import BaseModel

class PageInfoDto(BaseModel):
    total: int
    page_num: int
    size: int

    @classmethod
    def toDTO(cls, total: int, page_num: int, size: int) -> 'PageInfoDto':
        return cls(total=total, page_num=page_num, size=size)

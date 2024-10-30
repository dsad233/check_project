from pydantic import BaseModel, Field

class PageInfoDto(BaseModel):
    total: int = Field(default=0)
    page_num: int = Field(default=1)
    size: int = Field(default=10)

    @classmethod
    def toDTO(cls, total: int, page_num: int, size: int) -> 'PageInfoDto':
        return cls(total=total, page_num=page_num, size=size)

from fastapi import HTTPException, Depends
from app.middleware.tokenVerify import validate_token
from typing import Annotated
from app.models.models import Users


async def branch_check_admin(token : Annotated[Users, Depends(validate_token)]):
    try:

        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        return True
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail= "어드민 체크에 에러가 발생하였습니다.")


async def part_check_admin(token : Annotated[Users, Depends(validate_token)]):
    try:

        if token.role != "MSO 최고권한" | token.role != "최고관리자" | token.role != "관리자":
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        return True
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail= "어드민 체크에 에러가 발생하였습니다.")

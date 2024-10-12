from fastapi import HTTPException, Request
from sqlalchemy import select

from app.core.database import async_session
from app.middleware.jwt.jwtService import JWTDecoder, JWTService
from app.models.models import Users

users = async_session()


async def validate_token(req: Request):
    try:
        header = req.headers.get("Authorization")

        print(req.headers)

        if header == None:
            raise HTTPException(status_code=401, detail="로그인을 진행해주세요.")
        [tokenType, token] = header.split(" ")

        if tokenType != "Bearer":
            raise HTTPException(
                status_code=400, detail="토큰이 타입이 일치하지 않습니다."
            )
        if token == None:
            raise HTTPException(status_code=400, detail="토큰이 존재하지 않습니다.")
        jwtService = JWTService(None, JWTDecoder())
        jwtVerify = jwtService.check_token_expired(token)

        userId = jwtVerify.get("id")
        stmt = select(Users).where(Users.id == userId)
        result = await users.execute(stmt)
        findUser = result.scalar_one_or_none()
        if findUser == None:
            raise HTTPException(status_code=404, detail="유저가 존재하지 않습니다.")
        return findUser
    except HTTPException as http_err:
        print(f"HTTP 에러가 발생하였습니다: {http_err.detail}")
        raise  # 이 부분이 중요합니다. 예외를 다시 발생시켜 상위 호출자에게 전달합니다.
    except Exception as err:
        print(f"예상치 못한 에러가 발생하였습니다: {str(err)}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

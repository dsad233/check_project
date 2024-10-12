from fastapi import Depends, HTTPException, Request
from sqlalchemy import select

from app.core.database import async_session
from app.middleware.jwt.jwtService import JWTDecoder, JWTService
from app.models.models import Users

users = async_session()


async def validate_token(req: Request):
    header = req.cookies.get("authorization")

    if header == None:
        raise HTTPException(status_code=401, detail="로그인을 진행해주세요.")

    [tokenType, token] = header.split(" ")

    if tokenType != "Bearer":
        raise HTTPException(status_code=400, detail="토큰이 타입이 일치하지 않습니다.")

    if token is None:
        raise HTTPException(status_code=400, detail="토큰이 존재하지 않습니다.")

    jwtService = JWTService(None, JWTDecoder())

    try:
        jwtVerify = jwtService.check_token_expired(token)
    except:
        raise HTTPException(status_code=400, detail="토큰이 만료되었습니다.")

    userId = jwtVerify.get("id")

    query = select(Users).where(Users.id == userId)
    result = await users.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="유저가 존재하지 않습니다.")
    return user

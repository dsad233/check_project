from app.api.core.database import Session
from app.api.models.models import Users
from fastapi import Request, HTTPException
from app.api.middleware.jwt.jwtService import JWTService, JWTDecoder

db = Session()

async def vaildate_Token(req : Request):
    header = req.cookies.get('authorization')
    
    if(header == None):
        raise HTTPException(status_code=401, detail="로그인을 진행해주세요.") 
    [tokenType, token] = header.split(' ')

    if(tokenType != 'Bearer'):
        raise HTTPException(status_code=400, detail="토큰이 타입이 일치하지 않습니다.")
    if(token == None):
        raise HTTPException(status_code=400, detail="토큰이 존재하지 않습니다.")
    jwtService = JWTService(None, JWTDecoder())
    jwtVerify = jwtService.check_token_expired(token)
    
    userId = jwtVerify.get('id')
    findUser = db.query(Users).filter(Users.id == userId).first()
    if(findUser == None):
        raise HTTPException(status_code= 404, detail= "유저가 존재하지 않습니다.")
    return findUser
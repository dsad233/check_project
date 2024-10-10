from app.core.database import get_db
from app.api.routes.auth.schema.authSchema import Register, Login
from app.models.models import Users
from fastapi import APIRouter, Response, Depends
from fastapi.responses import JSONResponse
import bcrypt
from app.middleware.jwt.jwtService import JWTService, JWTEncoder, JWTDecoder
from typing import Annotated
from app.middleware.tokenVerify import vaildate_Token



router = APIRouter()
users = get_db()

# 패스워드 hash 함수
def hashPassword(password : str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))

# 비밀번호 비교
def verifyPassword(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

# 회원가입
@router.post('/register')
async def register(register: Register):
    try:
        findEmail = users.query(Users).filter(Users.email == register.email).first()
        findNickname = users.query(Users).filter(Users.nickname == register.nickname).first()

        if (findEmail):
            return JSONResponse(status_code= 400, content="이미 존재하는 이메일 입니다.")
        
        if(findNickname):
            return JSONResponse(status_code= 400, content="이미 존재하는 닉네임 입니다.")
        
        create = Users(
            email=register.email,
            password=hashPassword(register.password),
            nickname=register.nickname
        )

        users.add(create)
        users.commit()
        users.refresh(create)

        rolesCreate = Roles(
            userId = create.id
        )

        users.add(rolesCreate)
        users.commit()
        users.refresh(rolesCreate)

        return { "message": "유저를 정상적으로 생성하였습니다.", "data" : rolesCreate }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)



# 로그인
@router.post('/login')
async def login(login : Login, res : Response):
    try :
        findUser = users.query(Users).filter(Users.email == login.email).first()

        if (findUser == None):
            return JSONResponse(status_code= 404, content= "유저가 존재하지 않습니다.")
        
        if (not verifyPassword(login.password, findUser.password)):
            return JSONResponse(status_code= 400, content= "패스워드가 일치하지 않습니다.")
        
        jwt_service = JWTService(JWTEncoder(), JWTDecoder())

        jwtSign = jwt_service._create_token(data={ "id" : findUser.id })

        res.set_cookie('authorization', f'Bearer {jwtSign}')

        return { "message" : "로그인 완료" }

    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# 로그아웃
@router.post('/logout')
async def logout(res : Response, token : Annotated[Users, Depends(vaildate_Token)]):
    try:
        res.delete_cookie('authorization')
        return { "message" : "로그아웃 완료" }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.future import select

from app.api.routes.auth.schema.authSchema import Login, Register
from app.core.database import async_session, get_db
from app.middleware.jwt.jwtService import JWTDecoder, JWTEncoder, JWTService
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.users.users_model import Users
from app.enums.users import Role
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
# users = async_session()


# 패스워드 hash 함수
def hashPassword(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))


# 비밀번호 비교
def verifyPassword(password: str, hashed_password: str) -> bool:
    return password == hashed_password
    # return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


# 회원가입
# @router.post("/register")
# async def register(register: Register):
#     try:
#         findEmail = users.query(Users).filter(Users.email == register.email).first()
#         findNickname = (
#             users.query(Users).filter(Users.nickname == register.nickname).first()
#         )

#         if findEmail:
#             return JSONResponse(status_code=400, content="이미 존재하는 이메일 입니다.")

#         if findNickname:
#             return JSONResponse(status_code=400, content="이미 존재하는 닉네임 입니다.")

#         create = Users(
#             email=register.email,
#             password=hashPassword(register.password),
#             nickname=register.nickname,
#         )

#         users.add(create)
#         users.commit()
#         users.refresh(create)

#         rolesCreate = Roles(userId=create.id)

#         users.add(rolesCreate)
#         users.commit()
#         users.refresh(rolesCreate)

#         return {"message": "유저를 정상적으로 생성하였습니다.", "data": rolesCreate}
#     except Exception as err:
#         print("에러가 발생하였습니다.")
#         print(err)


# 로그인
@router.post("/login")
async def login(login: Login, res : Response, users: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Users).where(Users.email == login.email).where(Users.deleted_yn == "N")
        result = await users.execute(stmt)
        findUser = result.scalar_one_or_none()

        if findUser is None:
            return JSONResponse(status_code=404, content="유저가 존재하지 않습니다.")

        if not verifyPassword(login.password, findUser.password):
            return JSONResponse(
                status_code=400, content="패스워드가 일치하지 않습니다."
            )

        # 퇴사자/휴직자 체크
        if findUser.role in [Role.RESIGNED.value, Role.ON_LEAVE.value]:
            return JSONResponse(
                status_code=401,
                content="퇴사자 또는 휴직자는 로그인할 수 없습니다."
            )

        if findUser.role in [Role.TEMPORARY]:
            return JSONResponse(
                status_code=401,
                content="현재 임시 생성 상태입니다. 관리자의 승인을 기다려 주세요."
            )

        jwt_service = JWTService(JWTEncoder(), JWTDecoder())

        jwtToken = jwt_service._create_token(data={"id": findUser.id})

        res.set_cookie('Authorization', f'Bearer {jwtToken}')

        # 토큰을 응답 본문에 포함시켜 반환
        return JSONResponse(
            status_code=200,
            content={
                "message": "로그인 완료",
                "access_token": jwtToken,
                "token_type": "bearer",
            },
        )

    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        return JSONResponse(status_code=500, content="서버 오류가 발생했습니다.")


# 로그아웃
@router.post("/logout")
async def logout(res: Response):
    try:
        res.delete_cookie("Authorization")
        return {"message": "로그아웃 완료"}
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.routes.auth.auth import hashPassword
from app.api.routes.users.schema.userschema import UsersEdit
from app.core.database import get_db
from app.middleware.tokenVerify import validate_token
from app.models.models import Users

router = APIRouter(dependencies=[Depends(validate_token)])
users = get_db()


# 유저 전체 조회
@router.get("")
async def getUser():
    try:
        findAll = users.query(Users).all()
        if len(findAll) == 0:
            return JSONResponse(status_code=404, content="유저가 존재하지 않습니다.")
        return {
            "message": "유저를 정상적으로 전체 조회를 완료하였습니다.",
            "data": findAll,
        }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# 유저 상세 조회
@router.get("/{id}")
async def getOneUser(id: int):
    try:
        findOne = users.query(Users).filter(Users.id == id).first()

        if findOne == None:
            return JSONResponse(status_code=404, content="유저가 존재하지 않습니다.")

        return {
            "message": "유저를 정상적으로 전체 조회를 완료하였습니다.",
            "data": findOne,
        }

    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# 유저 정보 수정
@router.patch("/{id}")
async def updateUser(id: int, usersEdit: UsersEdit):
    try:
        findUser = users.query(Users).filter(Users.id == id).first()

        if findUser == None:
            return JSONResponse(status_code=404, content="유저가 존재하지 않습니다.")

        if findUser.nickname == usersEdit.nickname:
            return JSONResponse(status_code=400, content="이미 존재하는 닉네임 입니다.")

        findUser.password = hashPassword(usersEdit.password)
        findUser.nickname = usersEdit.nickname
        findUser.isOpen = (
            usersEdit.isOpen if (usersEdit.isOpen != None) else findUser.isOpen
        )
        findUser.image = (
            usersEdit.image if (usersEdit.image != None) else findUser.image
        )

        users.add(findUser)
        users.commit()

        return {"message": "유저를 정상적으로 수정하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# 유저 탈퇴
@router.delete("/{id}")
async def deleteUser(id: int):
    try:
        findUser = users.query(Users).filter(Users.id == id).first()

        if findUser == None:
            return JSONResponse(status_code=404, content="유저가 존재하지 않습니다.")

        users.delete(findUser)
        users.commit()

        return {"message": "유저를 정상적으로 삭제하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)

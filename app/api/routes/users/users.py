from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, update
from sqlalchemy.orm import load_only

from app.api.routes.auth.auth import hashPassword
from app.api.routes.users.schema.userschema import UserUpdate
from app.core.database import async_session, get_db
from app.middleware.tokenVerify import validate_token
from app.models.models import Users

router = APIRouter(dependencies=[Depends(validate_token)])
users = async_session()


# 유저 전체 조회
@router.get("")
async def get_users():
    try:
        # password를 제외한 모든 컬럼 선택
        stmt = select(Users).options(
            load_only(
                Users.id,
                Users.name,
                Users.email,
                Users.phone_number,
                Users.address,
                Users.education,
                Users.birth_date,
                Users.hire_date,
                Users.resignation_date,
                Users.gender,
                Users.part_id,
                Users.branch_id,
                Users.last_company,
                Users.last_position,
                Users.last_career_start_date,
                Users.last_career_end_date,
                Users.created_at,
                Users.updated_at,
                Users.deleted_yn,
            )
        )
        result = await users.execute(stmt)
        findAll = result.scalars().all()

        if not findAll:
            raise HTTPException(status_code=404, detail="유저가 존재하지 않습니다.")

        return {
            "message": "유저를 정상적으로 전체 조회를 완료하였습니다.",
            "data": findAll,
        }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 유저 상세 조회
@router.get("/{id}")
async def get_user_detail(id: int):
    try:
        # password를 제외한 모든 컬럼 선택
        stmt = (
            select(Users)
            .options(
                load_only(
                    Users.id,
                    Users.name,
                    Users.email,
                    Users.phone_number,
                    Users.address,
                    Users.education,
                    Users.birth_date,
                    Users.hire_date,
                    Users.resignation_date,
                    Users.gender,
                    Users.part_id,
                    Users.branch_id,
                    Users.last_company,
                    Users.last_position,
                    Users.last_career_start_date,
                    Users.last_career_end_date,
                    Users.created_at,
                    Users.updated_at,
                    Users.deleted_yn,
                )
            )
            .where(Users.id == id)
        )

        result = await users.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=404, detail="해당 ID의 유저가 존재하지 않습니다."
            )

        return {
            "message": "유저 상세 정보를 정상적으로 조회하였습니다.",
            "data": user,
        }
    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 유저 정보 수정
@router.patch("/{id}")
async def update_user(id: int, user_update: UserUpdate):
    try:
        # 업데이트할 필드만 선택
        update_data = user_update.dict(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=400, detail="업데이트할 정보가 제공되지 않았습니다."
            )

        # 유저 존재 여부 확인
        stmt = select(Users).where(Users.id == id)
        result = await users.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=404, detail="해당 ID의 유저가 존재하지 않습니다."
            )

        # 유저 정보 업데이트
        update_stmt = update(Users).where(Users.id == id).values(**update_data)
        await users.execute(update_stmt)
        await users.commit()

        # 업데이트된 유저 정보 조회 (비밀번호 제외)
        stmt = (
            select(Users)
            .options(
                load_only(
                    Users.id,
                    Users.name,
                    Users.email,
                    Users.phone_number,
                    Users.address,
                    Users.education,
                    Users.birth_date,
                    Users.hire_date,
                    Users.resignation_date,
                    Users.gender,
                    Users.part_id,
                    Users.branch_id,
                    Users.last_company,
                    Users.last_position,
                    Users.last_career_start_date,
                    Users.last_career_end_date,
                    Users.created_at,
                    Users.updated_at,
                    Users.deleted_yn,
                )
            )
            .where(Users.id == id)
        )
        result = await users.execute(stmt)
        updated_user = result.scalars().first()

        return {
            "message": "유저 정보가 성공적으로 업데이트되었습니다.",
            "data": updated_user,
        }
    except HTTPException as http_err:
        await users.rollback()
        raise http_err
    except Exception as err:
        await users.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# @router.patch("/{id}")
# async def updateUser(id: int, usersEdit: UsersEdit):
#     try:
#         findUser = users.query(Users).filter(Users.id == id).first()

#         if findUser == None:
#             return JSONResponse(status_code=404, content="유저가 존재하지 않습니다.")

#         if findUser.nickname == usersEdit.nickname:
#             return JSONResponse(status_code=400, content="이미 존재하는 닉네임 입니다.")

#         findUser.password = hashPassword(usersEdit.password)
#         findUser.nickname = usersEdit.nickname
#         findUser.isOpen = (
#             usersEdit.isOpen if (usersEdit.isOpen != None) else findUser.isOpen
#         )
#         findUser.image = (
#             usersEdit.image if (usersEdit.image != None) else findUser.image
#         )

#         users.add(findUser)
#         users.commit()

#         return {"message": "유저를 정상적으로 수정하였습니다."}
#     except Exception as err:
#         print("에러가 발생하였습니다.")
#         print(err)


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

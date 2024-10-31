from fastapi import APIRouter, HTTPException, Depends
from app.models.users.users_model import Users
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.middleware.tokenVerify import validate_token, get_current_user
from app.core.database import async_session, get_db
from typing import Annotated
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, load_only
from app.middleware.mailsend import send_email, MailSend
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()
# mailsend = async_session()


# 메일 발송
@router.post('/mailsend')
async def create_mail_send(mailSend : MailSend):
    try:
        await send_email(mailSend.to_email, mailSend.title, mailSend.context)  
        
        return { "message" : "성공적으로 메일을 발송 하였습니다." }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송에 실패하였습니다.")


# 메일 발송 기록 전체 조회
@router.get("/mailsend")
async def get_mailsend_all(token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]

        return { "message" : "성공적으로 메일 발송 기록 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 전체 조회에 실패하였습니다.")


""" 지점별 """
# 메일 발송 기록 지점별 전체 조회
@router.get("/{branch_id}/mailsend")
async def get_branch_mailsend_all(branch_id : int, token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]

        return { "message" : "성공적으로 메일 발송 기록 지점별 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 지점별 전체 조회에 실패하였습니다.")
    

# 메일 발송 기록 지점별 이름 전체 조회
@router.get("/{branch_id}/mailsend/name")
async def get_branch_mailsend_name(branch_id : int, name : str, token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Users.name.like(f'%{name}%'), Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]

        return { "message" : "성공적으로 메일 발송 기록 이름으로 지점별 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 이름으로 지점별 전체 조회에 실패하였습니다.")
    

# 메일 발송 기록 지점별 이메일 전체 조회
@router.get("/{branch_id}/mailsend/email")
async def get_branch_mailsend_email(branch_id : int, email : str, token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Users.email.like(f'%{email}%'), Branches.id == branch_id, Branches.deleted_yn == "N", Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]

        return { "message" : "성공적으로 메일 발송 기록 이메일로 지점별 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 이메일로 지점별 전체 조회에 실패하였습니다.")

""" 파트별 """
# 메일 발송 기록 파트별 전체 조회
@router.get("/{branch_id}/parts/{part_id}/mailsend")
async def get_part_mailsend_all(branch_id : int, part_id : int , token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]

        return { "message" : "성공적으로 메일 발송 기록 파트별 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 파트별 전체 조회에 실패하였습니다.")
    

# 메일 발송 기록 파트별 상세 조회
@router.get("/{branch_id}/parts/{part_id}/mailsend/{id}")
async def get_part_mailsend_id(branch_id : int, part_id : int, id : int, token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]
        return { "message" : "성공적으로 메일 발송 기록 파트별 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 파트별 전체 조회에 실패하였습니다.")

# 메일 발송 기록 지점별 이름 전체 조회
@router.get("/{branch_id}/parts/{part_id}/mailsend/name")
async def get_part_mailsend_name(branch_id : int, part_id : int, name : str, token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Users.name.like(f'%{name}%'), Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]

        return { "message" : "성공적으로 메일 발송 기록 이름으로 파트별 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 이름으로 파트별 전체 조회에 실패하였습니다.")
    


# 메일 발송 기록 지점별 이메일 전체 조회
@router.get("/{branch_id}/parts/{part_id}/mailsend/email")
async def get_part_mailsend_email(branch_id : int, part_id : int, email : str, token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Users.email.like(f'%{email}%'), Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchsall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]

        return { "message" : "성공적으로 메일 발송 기록 이메일로 파트별 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 이메일로 파트별 전체 조회에 실패하였습니다.")
    


""" 유저별 """
# 메일 발송 기록 유저별 전체 조회
@router.get("/{branch_id}/parts/{part_id}/mailsend/users/{user_id}")
async def get_user_mailsend_all(branch_id : int, part_id : int, user_id : int, token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Users.id == user_id, Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]

        return { "message" : "성공적으로 메일 발송 기록 유저별 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 유저별 전체 조회에 실패하였습니다.")
    



# 메일 발송 기록 유저별 이름 전체 조회
@router.get("/{branch_id}/parts/{part_id}/mailsend/{user_id}/name")
async def get_user_mailsend_name(branch_id : int, part_id : int, name : str, token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Users.name.like(f'%{name}%'), Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]

        return { "message" : "성공적으로 메일 발송 기록 이름으로 유저별 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 이름으로 유저별 전체 조회에 실패하였습니다.")
    



# 메일 발송 기록 지점별 이메일 전체 조회
@router.get("/{branch_id}/parts/{part_id}/mailsend/{user_id}/email")
async def get_user_mailsend_email(branch_id : int, part_id : int, email : str, token:Annotated[Users, Depends(get_current_user)], mailsend: AsyncSession = Depends(get_db)):
    try:
        find_all_user = await mailsend.execute(select(Users, Branches, Parts).join(Users.branch_id == Branches.id).join(Users.part_id == Parts.id).options(load_only(Users.id, Users.name, Users.gender, Users.birth_date, Users.hire_date, Users.email), load_only(Parts.name)).where(Users.email.like(f'%{email}%'), Branches.id == branch_id, Branches.deleted_yn == "N", Parts.id == part_id, Parts.deleted_yn == "N", Users.deleted_yn == "N").order_by(Users.name.asc()).offset(0).limit(100))
        result_user = find_all_user.fetchsall()
        
        fetch_data = [
            {
                "users" : { "id" : data.Users.id, "name": data.Users.name, "gender": data.Users.gender, "birth_date" : data.Users.birth_date, "hire_date" : data.Users.hire_date, "email" : data.Users.email },
                "parts" : { "part_name" : data.Parts.name }
            }
            for data in result_user
        ]

        return { "message" : "성공적으로 메일 발송 기록 이메일로 유저별 전체 조회를 하였습니다.", "data" : fetch_data }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="메일 발송 기록 이메일로 유저별 전체 조회에 실패하였습니다.")
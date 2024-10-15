from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, aliased
from datetime import datetime

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.users.posts_model import Posts, PostsResponse, PostListResponse, PostsCreate, PostsUpdate, PostsSearchDto
from app.models.users.users_model import Users
from app.models.branches.board_model import Board
from app.common.dto.pagination_dto import PaginationDto

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

@router.get("", response_model=PostListResponse)
async def get_posts(
    branch_id: int, board_id: int, search: PostsSearchDto = Depends(), current_user_id: int = Depends(get_current_user_id)
) -> PostListResponse:
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()
        
        if current_user.role.strip() != "MSO 최고권한" and current_user.branch_id != branch_id :
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        board_query = select(Board).where(Board.id == board_id, Board.branch_id == branch_id, Board.deleted_yn == 'N')
        board_result = await db.execute(board_query)
        board = board_result.scalar_one_or_none()

        if board is None:
            raise HTTPException(status_code=404, detail="게시판이 존재하지 않습니다.")
        
        check_authority(current_user.role.strip(), board.read_authority.strip())
        
        count_query = select(func.count()).select_from(Posts).where(Posts.branch_id == branch_id, Posts.board_id == board_id, Posts.deleted_yn == 'N')
        count_result = await db.execute(count_query)
        count = count_result.scalar_one_or_none()
        
        pagination = PaginationDto(total_record=count)


        query = select(Posts).join(Users, Posts.user_id == Users.id).options(joinedload(Posts.users)).offset(search.offset).limit(search.record_size).where(
            Posts.branch_id == branch_id, 
            Posts.board_id == board_id, 
            Posts.deleted_yn == 'N'
        )
        
        if search.title is not None:
            query = query.where(Posts.title.like(f"%{search.title}%"))
        if search.content is not None:
            query = query.where(Posts.content.like(f"%{search.content}%"))
        if search.author_name is not None:
            query = query.where(Users.name.like(f"%{search.author_name}%"))
        
        result = await db.execute(query)
        getPost = result.scalars().all()

        posts_response = [PostsResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            author_name=post.users.name
        ) for post in getPost]
        
        post_list_response = PostListResponse(list=posts_response, pagination=pagination)

        return post_list_response
    except Exception as err:
        print("에러가 발생하였습니다.", err)
        raise HTTPException(status_code=500, detail=str(err))

@router.get("/{post_id}", response_model=PostsResponse)
async def get_post(
    branch_id: int, board_id: int, post_id: int, current_user_id: int = Depends(get_current_user_id)
) -> PostsResponse:
    try:
        user_query = select(Users).options(joinedload(Users.part)).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()
        
        if current_user.role.strip() != "MSO 최고권한" and current_user.branch_id != branch_id :
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        board_query = select(Board).where(Board.id == board_id, Board.branch_id == branch_id, Board.deleted_yn == 'N')
        board_result = await db.execute(board_query)
        board = board_result.scalar_one_or_none()
        
        check_authority(current_user.role.strip(), board.read_authority.strip())

        query = select(Posts).where(Posts.id == post_id, Posts.branch_id == branch_id, Posts.board_id == board_id, Posts.deleted_yn == 'N')
        result = await db.execute(query)
        postOne = result.scalar_one_or_none()

        if postOne is None:
            raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")
        
        create_post_response = PostsResponse(
            id=postOne.id,
            title=postOne.title,
            content=postOne.content,
            author_name=postOne.users.name,
            created_at=postOne.created_at
        )

        return create_post_response
    except Exception as err:
        print("에러가 발생하였습니다.", err)
        raise HTTPException(status_code=500, detail=str(err))

@router.post("", status_code=201)
async def create_post(
    branch_id: int, board_id: int, postCreate: PostsCreate, current_user_id: int = Depends(get_current_user_id)
):
    try:
        user_query = select(Users).options(joinedload(Users.part)).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()
        
        if current_user.role.strip() != "MSO 최고권한" and current_user.branch_id != branch_id :
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        board_query = select(Board).where(Board.id == board_id, Board.branch_id == branch_id, Board.deleted_yn == 'N')
        board_result = await db.execute(board_query)
        board = board_result.scalar_one_or_none()

        check_authority(current_user.role.strip(), board.write_authority.strip())

        create = Posts(
            user_id=current_user.id,
            board_id=board_id,
            branch_id=branch_id,
            
            title=postCreate.title,
            content=postCreate.content,
        )

        db.add(create)
        await db.commit()

        return {"message": "게시글을 정상적으로 생성하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.", err)
        raise HTTPException(status_code=500, detail=str(err))

@router.patch("/{post_id}")
async def update_post(
    branch_id: int, board_id: int, post_id: int, posts_update: PostsUpdate, current_user_id: int = Depends(get_current_user_id)
):
    try:
        user_query = select(Users).options(joinedload(Users.part)).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()
        
        if current_user.role.strip() != "MSO 최고권한" and current_user.branch_id != branch_id :
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        board_query = select(Board).where(Board.id == board_id, Board.branch_id == branch_id, Board.deleted_yn == 'N')
        board_result = await db.execute(board_query)
        board = board_result.scalar_one_or_none()

        check_authority(current_user.role.strip(), board.write_authority.strip())

        query = select(Posts).where(Posts.id == post_id, Posts.branch_id == branch_id, Posts.board_id == board_id, Posts.deleted_yn == 'N')
        result = await db.execute(query)
        postOne = result.scalar_one_or_none()

        if postOne is None:
            raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")
        
        if postOne.users.id != current_user.id:
            raise HTTPException(status_code=403, detail="작성자가 아닙니다.")

        if posts_update.title is not None:
            postOne.title = posts_update.title
        if posts_update.content is not None:
            postOne.content = posts_update.content

        postOne.updated_at = datetime.now()
        await db.commit()

        return {"message": "게시글을 정상적으로 수정하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.", err)
        raise HTTPException(status_code=500, detail=str(err))

@router.delete("/{post_id}")
async def delete_post(
    branch_id: int, board_id: int, post_id: int, current_user_id: int = Depends(get_current_user_id)
):
    try:
        user_query = select(Users).options(joinedload(Users.part)).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()
        
        if current_user.role.strip() != "MSO 최고권한" and current_user.branch_id != branch_id :
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        board_query = select(Board).where(Board.id == board_id, Board.branch_id == branch_id, Board.deleted_yn == 'N')
        board_result = await db.execute(board_query)
        board = board_result.scalar_one_or_none()

        check_authority(current_user.role.strip(), board.write_authority.strip())

        query = select(Posts).where(Posts.id == post_id, Posts.branch_id == branch_id, Posts.board_id == board_id, Posts.deleted_yn == 'N')
        result = await db.execute(query)
        postOne = result.scalar_one_or_none()

        if postOne is None:
            raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")
        
        if postOne.users.id != current_user.id:
            raise HTTPException(status_code=403, detail="작성자가 아닙니다.")
        
        postOne.deleted_yn = 'Y'
        postOne.updated_at = datetime.now()
        await db.commit()

        return {"message": "게시글을 정상적으로 삭제하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.", err)
        raise HTTPException(status_code=500, detail=str(err))

def check_authority(user_role:str, board_role:str):
    
    if (board_role == 'MSO 최고권한' and user_role != 'MSO 최고권한') or \
       (board_role == '최고관리자' and user_role not in ['최고관리자', 'MSO 최고권한']) or \
       (board_role == '관리자' and user_role not in ['관리자', '최고관리자', 'MSO 최고권한']) or \
       (user_role == '퇴사자'):
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

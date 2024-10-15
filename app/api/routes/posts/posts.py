from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from datetime import datetime
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.users.posts_model import Posts, PostsResponse, PostListResponse, PostsCreate, PostsUpdate
from app.models.users.users_model import Users
from app.models.branches.board_model import Board
from app.common.dto.search_dto import BaseSearchDto
from app.common.dto.pagination_dto import PaginationDto

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

# 게시글 전체 조회
@router.get("", response_model=PostListResponse)
async def getAllPost(
    branch_id: int, board_id: int, search: BaseSearchDto = Depends(), current_user_id: int = Depends(get_current_user_id)
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

        query = select(Posts).options(joinedload(Posts.users)).offset(search.offset).limit(search.record_size).where(Posts.branch_id == branch_id, Posts.board_id == board_id, Posts.deleted_yn == 'N')
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


# 게시글 상세 조회
@router.get("/{post_id}", response_model=PostsResponse)
async def getOnePost(
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


# 게시글 생성
@router.post("")
async def postCreate(
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


# 게시글 수정
@router.patch("/{id}")
async def postEdit(id: int, postsEdit: PostsUpdate):
    try:

        findPost = db.query(Posts).filter(Posts.id == id).first()

        if findPost == None:
            raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")

        findPost.title = postsEdit.title
        findPost.context = postsEdit.context
        findPost.category = (
            postsEdit.category if (postsEdit.category != None) else findPost.category
        )
        findPost.isOpen = (
            postsEdit.isOpen if (postsEdit.isOpen != None) else findPost.isOpen
        )
        findPost.image = (
            postsEdit.image if (postsEdit.image != None) else findPost.image
        )

        return {"message": "게시글을 정상적으로 수정하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.", err)
        raise HTTPException(status_code=500, detail=str(err))


# 게시글 삭제
@router.delete("/{id}")
async def postDelete(id: int):
    try:
        findPost = db.query(Posts).filter(Posts.id == id).first()

        if findPost == None:
            raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")

        db.delete(findPost)
        db.commit()

        return {"message": "게시글을 정상적으로 삭제하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.", err)
        raise HTTPException(status_code=500, detail=str(err))

def check_authority(user_role_enum:str, board_role_enum:str):
    
    if board_role_enum.strip() == 'MSO 최고권한':
        if user_role_enum.strip() != 'MSO 최고권한':
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
    if board_role_enum.strip() == '최고관리자':
        if user_role_enum.strip() not in ['최고관리자', 'MSO 최고권한']:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
    if board_role_enum.strip() == '관리자':
        if user_role_enum.strip() not in ['관리자', '최고관리자', 'MSO 최고권한']:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
    if board_role_enum.strip() == '사원':
        if user_role_enum.strip() == '퇴사자':
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
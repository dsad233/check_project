from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.api.routes.posts.schema.postschema import PostCreate, PostsEdit
from app.core.database import get_db
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.users.posts_model import Posts, PostsResponse
from app.models.users.users_model import Users
from app.models.branches.board_model import Board
from sqlalchemy.orm import joinedload

router = APIRouter(dependencies=[Depends(validate_token)])
posts = get_db()


# 게시글 전체 조회
@router.get("", response_model=list[PostsResponse])
async def getAllPost(branch_id: int, board_id: int, current_user_id: int = Depends(get_current_user_id)):
    try:
        user_query = select(Users).options(joinedload(Users.part)).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await posts.execute(user_query)
        current_user = user_result.scalar_one_or_none()
        
        if current_user is None:
            return JSONResponse(status_code=404, content="유저가 존재하지 않습니다.")
        
        board_query = select(Board).where(Board.id == board_id, Board.branch_id == branch_id, Board.deleted_yn == 'N')
        board_result = await posts.execute(board_query)
        board = board_result.scalar_one_or_none()
        
        if board is None:
            return JSONResponse(status_code=404, content="게시판이 존재하지 않습니다.")
        
        if board.read_authority.strip() == 'MSO 최고권한':
            if current_user.role.strip() != 'MSO 최고권한':
                return JSONResponse(status_code=403, content="권한이 없습니다.")
        if board.read_authority.strip() == '최고관리자':
            if current_user.role.strip() not in ['최고관리자', 'MSO 최고권한']:
                return JSONResponse(status_code=403, content="권한이 없습니다.")
        if board.read_authority.strip() == '관리자':
            if current_user.role.strip() not in ['관리자', '최고관리자', 'MSO 최고권한']:
                return JSONResponse(status_code=403, content="권한이 없습니다.")
        if board.read_authority.strip() == '사원':
            if current_user.role.strip() == '퇴사자':
                return JSONResponse(status_code=403, content="권한이 없습니다.")
        
        query = select(Posts).where(Posts.branch_id == branch_id, Posts.board_id == board_id, Posts.deleted_yn == 'N')
        result = await posts.execute(query)
        getPost = result.scalars().all()

        posts_response = [PostsResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            created_at=post.created_at
        ) for post in getPost]

        return posts_response
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# 게시글 상세 조회
@router.get("/{id}")
async def getOnePost(id: int):
    try:
        postOne = posts.query(Posts).filter(Posts.id == id).first()

        if postOne == None:
            return JSONResponse(status_code=404, content="게시글이 존재하지 않습니다.")

        return {"message": "게시글 상세 조회에 성공하였습니다.", "data": postOne}
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# 게시글 생성
@router.post("")
async def postCreate(postCreate: PostCreate):
    try:
        create = Posts(
            title=postCreate.title,
            context=postCreate.context,
            category=postCreate.category,
            isOpen=postCreate.isOpen,
            image=postCreate.image,
        )

        posts.add(create)
        posts.commit()
        posts.refresh(create)

        return {"message": "게시글을 정상적으로 생성하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# 게시글 수정
@router.patch("/{id}")
async def postEdit(id: int, postsEdit: PostsEdit):
    try:

        findPost = posts.query(Posts).filter(Posts.id == id).first()

        if findPost == None:
            return JSONResponse(status_code=404, content="게시글이 존재하지 않습니다.")

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
        print("에러가 발생하였습니다.")
        print(err)


# 게시글 삭제
@router.delete("/{id}")
async def postDelete(id: int):
    try:
        findPost = posts.query(Posts).filter(Posts.id == id).first()

        if findPost == None:
            return JSONResponse(status_code=404, content="게시글이 존재하지 않습니다.")

        posts.delete(findPost)
        posts.commit()

        return {"message": "게시글을 정상적으로 삭제하였습니다."}
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)

from app.core.database import get_db
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.api.middleware.tokenVerify import vaildate_Token
from app.api.models.models import Posts
from app.api.routes.posts.schema.postsSchema import PostCreate, PostsEdit


router = APIRouter(dependencies=[Depends(vaildate_Token)])
posts = get_db()

# 게시글 전체 조회
@router.get('')
async def getAllPost():
    try:
        getPost = posts.query(Posts).all()

        if(len(getPost) == 0):
            return JSONResponse(status_code= 404, content="게시글들이 존재하지 않습니다.")
        
        return { "message" : "게시글 전체 조회에 성공하였습니다.", "data" : getPost }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# 게시글 상세 조회
@router.get('/{id}')
async def getOnePost(id : int):
    try:
        postOne = posts.query(Posts).filter(Posts.id == id).first()

        if(postOne == None):
            return JSONResponse(status_code=404, content="게시글이 존재하지 않습니다.")
        
        return { "message" : "게시글 상세 조회에 성공하였습니다.", "data" : postOne }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# 게시글 생성
@router.post('')
async def postCreate(postCreate : PostCreate):
    try:
        create = Posts(
            title = postCreate.title,
            context = postCreate.context,
            category = postCreate.category,
            isOpen = postCreate.isOpen,
            image = postCreate.image
        )

        posts.add(create)
        posts.commit()
        posts.refresh(create)
        
        return { "message" : "게시글을 정상적으로 생성하였습니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)



# 게시글 수정
@router.patch('/{id}')
async def postEdit(id : int, postsEdit : PostsEdit):
    try:
        
        findPost = posts.query(Posts).filter(Posts.id == id).first()

        if(findPost == None):
            return JSONResponse(status_code=404, content="게시글이 존재하지 않습니다.")
        
        findPost.title = postsEdit.title
        findPost.context = postsEdit.context
        findPost.category = postsEdit.category if(postsEdit.category != None) else findPost.category
        findPost.isOpen = postsEdit.isOpen if(postsEdit.isOpen != None) else findPost.isOpen
        findPost.image = postsEdit.image if(postsEdit.image != None) else findPost.image
        
        return { "message" : "게시글을 정상적으로 수정하였습니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# 게시글 삭제
@router.delete('/{id}')
async def postDelete(id : int):
    try:
        findPost = posts.query(Posts).filter(Posts.id == id).first()

        if(findPost == None):
            return JSONResponse(status_code=404, content="게시글이 존재하지 않습니다.")
        
        posts.delete(findPost)
        posts.commit()

        return { "message": "게시글을 정상적으로 삭제하였습니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)

    
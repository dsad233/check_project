from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.users.comments_model import Comments, CommentsResponse, CommentsCreate, CommentsUpdate
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

@router.get("", response_model=CommentsResponse)
async def get_comments(
    board_id: int, 
    post_id: int, 
    search: BaseSearchDto = Depends(), 
    current_user_id: int = Depends(get_current_user_id)
) -> CommentsResponse:
    try:
        pass
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{comment_id}", response_model=CommentsResponse)
async def getOneComment(
    board_id: int, 
    post_id: int, 
    comment_id: int, 
    current_user_id: int = Depends(get_current_user_id)
) -> CommentsResponse:
    try:
        pass
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", status_code=201)
async def postCreate(
    board_id: int, 
    post_id: int, 
    commentCreate: CommentsCreate, 
    current_user_id: int = Depends(get_current_user_id)
):
    try:
        pass
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) 

@router.patch("/{comment_id}", response_model=CommentsResponse)
async def putUpdate(
    board_id: int, 
    post_id: int, 
    comment_id: int, 
    commentUpdate: CommentsUpdate, 
    current_user_id: int = Depends(get_current_user_id)
):
    try:
        pass
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{comment_id}")
async def deleteDelete(
    board_id: int, 
    post_id: int, 
    comment_id: int, 
    current_user_id: int = Depends(get_current_user_id)
):
    try:
        pass
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

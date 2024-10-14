from fastapi import APIRouter, Depends, HTTPException
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.branches.board_model import Board, BoardResponse, BoardCreate, BoardUpdate
from sqlalchemy import select
from app.models.users.users_model import Users

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

@router.get("/", response_model=list[BoardResponse])
async def get_board(branch_id: int):
    try:        
        query = select(Board).where(Board.branch_id == branch_id, Board.deleted_yn == 'N')
        result = await db.execute(query)
        boards = result.scalars().all()
        
        board_response = [BoardResponse(
            id=board.id,
            category_name=board.category_name,
            description=board.description,
            read_authority=board.read_authority,
            write_authority=board.write_authority,
            notice_authority=board.notice_authority,
            part_division=board.part_division,
            allow_comment=board.allow_comment
        ) for board in boards]
        
        return board_response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_board(branch_id: int, create_dto: BoardCreate, current_user_id: int = Depends(get_current_user_id)):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if user.role.strip() not in ['MSO 최고권한', '최고관리자']:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        board_query = select(Board).where(Board.branch_id == branch_id, Board.category_name == create_dto.category_name, Board.deleted_yn == 'N')
        board_result = await db.execute(board_query)
        board = board_result.scalar_one_or_none()
        
        if board:
            raise HTTPException(status_code=400, detail="Board already exists")
        
        new_board = Board(
            branch_id=branch_id,
            category_name=create_dto.category_name,
            division=create_dto.division
        )
        
        db.add(new_board)
        await db.commit()
        
        return {"message": "Board created successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/{category_id}")
async def update_board(branch_id: int, category_id: int, update_dto: BoardUpdate, current_user_id: int = Depends(get_current_user_id)):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if user.role.strip() not in ['MSO 최고권한', '최고관리자']:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        if update_dto.category_name:
            validate_query = select(Board).where(Board.category_name == update_dto.category_name, Board.branch_id == branch_id, Board.deleted_yn == 'N', Board.id != category_id)
            validate_result = await db.execute(validate_query)
            validate_category = validate_result.scalar_one_or_none()
            
            if validate_category:
                raise HTTPException(status_code=400, detail="Board already exists")
        
        board_query = select(Board).where(Board.id == category_id, Board.branch_id == branch_id, Board.deleted_yn == 'N')
        board_result = await db.execute(board_query)
        board = board_result.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        if update_dto.category_name:
            board.category_name = update_dto.category_name
        if update_dto.division != board.division:
            board.division = update_dto.division
        
        await db.commit()
        
        return {"message": "Board updated successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{category_id}")
async def delete_board(branch_id: int, category_id: int, current_user_id: int = Depends(get_current_user_id)):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if user.role.strip() not in ['MSO 최고권한', '최고관리자']:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        board_query = select(Board).where(Board.id == category_id, Board.branch_id == branch_id, Board.deleted_yn == 'N')
        board_result = await db.execute(board_query)
        board = board_result.scalar_one_or_none()
        
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        board.deleted_yn = 'Y'
        await db.commit()
        
        return {"message": "Board deleted successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends
from app.middleware.tokenVerify import validate_token
from app.api.routes.parts.schema.partsSchema import PartCreate
from app.core.database import async_session
from app.models.models import Users, Parts, Branches
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
router = APIRouter(dependencies=[Depends(validate_token)])
parts = async_session()

@router.get('')
async def getParts(
    current_user: Users = Depends(validate_token)
):
    try:
        if current_user.role.name != 'MSO 최고권한' and current_user.role.name != '최고관리자':
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        query = select(Parts).where(Parts.branch_id == current_user.branch_id)
        result = await parts.execute(query)
        parts = result.scalars().all()
        return { "message" : "부서 조회에 성공하였습니다.", "data" : parts }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다") 
    
@router.post('')
async def createPart(
    part: PartCreate,
    current_user: Users = Depends(validate_token)
):
    try: 
        if current_user.role.name != 'MSO 최고권한' and current_user.role.name != '최고관리자' and current_user.branch_id != part.branch_id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        branch_query = select(Branches).where(Branches.id == part.branch_id)
        branch_result = await parts.execute(branch_query)
        branch = branch_result.scalars().first()
        
        if not branch:
            raise HTTPException(status_code=400, detail="존재하지 않는 지점입니다.")
        
        query = insert(Parts).values(part.model_dump())
        await parts.execute(query)
        await parts.commit()
        
        return { "message" : "부서 생성에 성공하였습니다." }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다") 
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.branches.human_record_category_model import HumanRecordCategory, HumanRecordCategoryResponse, HumanRecordCategoryCreate, HumanRecordCategoryUpdate
from sqlalchemy import select
from app.models.users.users_model import Users

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

@router.get("/", response_model=list[HumanRecordCategoryResponse])
async def get_human_record_category(branch_id: int, current_user_id: int = Depends(get_current_user_id)):
    
    try:
        user_query = select(Users).where(Users.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if user.role.strip() != 'MSO 관리자' and user.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        query = select(HumanRecordCategory).where(HumanRecordCategory.branch_id == branch_id, HumanRecordCategory.deleted_yn == 'N')
        result = await db.execute(query)
        human_record_categories = result.scalars().all()
        
        human_record_category_response = [HumanRecordCategoryResponse(
            id=category.id,
            category_name=category.category_name,
            division=category.division
        ) for category in human_record_categories]
        
        return human_record_category_response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_human_record_category(branch_id: int, create_dto: HumanRecordCategoryCreate, current_user_id: int = Depends(get_current_user_id)):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if user.role.strip() not in ['MSO 관리자', '최고관리자']:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        hr_query = select(HumanRecordCategory).where(HumanRecordCategory.branch_id == branch_id, HumanRecordCategory.category_name == create_dto.category_name, HumanRecordCategory.deleted_yn == 'N')
        hr_result = await db.execute(hr_query)
        hr_category = hr_result.scalar_one_or_none()
        
        if hr_category:
            raise HTTPException(status_code=400, detail="Human record category already exists")
        
        new_category = HumanRecordCategory(
            branch_id=branch_id,
            category_name=create_dto.category_name,
            division=create_dto.division
        )
        
        db.add(new_category)
        await db.commit()
        
        return {"message": "Human record category created successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/{category_id}")
async def update_human_record_category(branch_id: int, category_id: int, update_dto: HumanRecordCategoryUpdate, current_user_id: int = Depends(get_current_user_id)):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if user.role.strip() not in ['MSO 관리자', '최고관리자']:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        if update_dto.category_name:
            validate_query = select(HumanRecordCategory).where(HumanRecordCategory.category_name == update_dto.category_name, HumanRecordCategory.branch_id == branch_id, HumanRecordCategory.deleted_yn == 'N', HumanRecordCategory.id != category_id)
            validate_result = await db.execute(validate_query)
            validate_category = validate_result.scalar_one_or_none()
            
            if validate_category:
                raise HTTPException(status_code=400, detail="Human record category already exists")
        
        hr_query = select(HumanRecordCategory).where(HumanRecordCategory.id == category_id, HumanRecordCategory.branch_id == branch_id, HumanRecordCategory.deleted_yn == 'N')
        hr_result = await db.execute(hr_query)
        hr_category = hr_result.scalar_one_or_none()
        
        if not hr_category:
            raise HTTPException(status_code=404, detail="Human record category not found")
        
        if update_dto.category_name:
            hr_category.category_name = update_dto.category_name
        if update_dto.division != hr_category.division:
            hr_category.division = update_dto.division
        
        await db.commit()
        
        return {"message": "Human record category updated successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{category_id}")
async def delete_human_record_category(branch_id: int, category_id: int, current_user_id: int = Depends(get_current_user_id)):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if user.role.strip() not in ['MSO 관리자', '최고관리자']:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        hr_query = select(HumanRecordCategory).where(HumanRecordCategory.id == category_id, HumanRecordCategory.branch_id == branch_id, HumanRecordCategory.deleted_yn == 'N')
        hr_result = await db.execute(hr_query)
        hr_category = hr_result.scalar_one_or_none()
        
        if not hr_category:
            raise HTTPException(status_code=404, detail="Human record category not found")
        
        hr_category.deleted_yn = 'Y'
        await db.commit()
        
        return {"message": "Human record category deleted successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

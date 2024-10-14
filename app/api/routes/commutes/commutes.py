from fastapi import APIRouter, Depends, HTTPException
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.api.routes.commutes.schema.commute_schema import CommuteCreate, CommuteResponse
from app.core.database import async_session
from app.models.models import Commutes

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

@router.post("", response_model=CommuteResponse)
async def create_clock_in(
    commute: CommuteCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    try:
        new_commute = Commutes(
            user_id=current_user_id,
            clock_in=commute.clock_in,
        )

        db.add(new_commute)
        await db.commit()
        await db.refresh(new_commute)

        return CommuteResponse(
            id=new_commute.id,
            user_id=new_commute.user_id,
            clock_in=new_commute.clock_in,
            clock_out=new_commute.clock_out,
            work_hours=new_commute.work_hours,
            updated_at=new_commute.updated_at,
            deleted_yn=new_commute.deleted_yn
        )
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
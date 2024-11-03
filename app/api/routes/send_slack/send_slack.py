from fastapi import APIRouter, HTTPException
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.slack_utils import SlackAPI


router = APIRouter()

# 슬랙 메시지 전송
@router.post("")
async def send_slakc_message(token : str, context : str):
    try:
        channel_id = "D07Q87U8Z1V"
        SlackAPI(token=token)
        await SlackAPI.post_message(channel_id=channel_id, text=context)

        return {"message" : "정상적으로 슬랙 메시지가 전송되었습니다."}
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail={f"슬랙 메시지 전송에 싪하였습니다. : {str(err)}"})



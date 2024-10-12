from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.models.models import Overtime
from fastapi.responses import JSONResponse
from typing import Annotated
from sqlalchemy.future import select
# from app.api.routes.overtimes.schema.overtimeschema import OverTimeCrete, OverTimeEdit

router = APIRouter(dependencies=Annotated[Overtime,Depends(validate_token)])
overtime = async_session()


data = {
    "overtime_id" : 1,
    "application_date" : 32,
    "application_note" : 32,
    "proposer_note" : 32
}

# overtime 전체 조회
@router.get("")
async def find_all():
    try :
        overtimeall = await overtime.execute(select(Overtime))
        result = overtimeall.scalar()

        if(len(overtimeall) == 0):
            return JSONResponse(status_code= 404, content="타임 데이터가 존재하지 않습니다.")
        
        return { "message" : "오버타임 데이터 전체 조회에 성공하였습니다.", "data" : result }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)

# overtime 지점애 따라 조회
@router.get('/{spot}')
async def find_spot():
    try:
        find_spot = overtime.query(Overtime).filter()

        if(find_spot == None):
            return JSONResponse(status_code= 404, content="타임 데이터가 존재하지 않습니다.")

        return { "message" : "지점별 오버타임 전체 조회에 성공하였습니다.", "data" : find_spot }
    except Exception as err:
        print("에러가 발생하였습니다.")    
        print(err)


# overtime 상세 조회
@router.get("/{id}")
async def find_one():
    try:
        overtimeone = (
            await overtime.query(Overtime).filter(Overtime.manager_id == id).first()
        )

        if overtimeone == None:
            return JSONResponse(
                status_code=404, content="타임 데이터가 존재하지 않습니다."
            )

        return {
            "message": "오버타임 데이터 전체 조회에 성공하였습니다.",
            "data": overtimeone,
        }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# overtime 생성
@router.post('')
async def time_create(schema : OverTimeCrete, token : Annotated[Overtime, Depends(validate_token)]):
    try :
        
        overtimecreate = Overtime(
            proposer_id = token.id,
            application_note = schema.application_note                                                                      
        )                                   
        
        overtime.add(overtimecreate)
        overtime.commit()                                        
        overtime.refresh(overtimecreate)

        
        return { "message" : "오버타임 데이터 요청에 성공하였습니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# overtime 수정 [어드민만]
@router.patch('/{id}')
async def time_edit(id : int, schema : OverTimeEdit, token : Annotated[Overtime, Depends(validate_token)]):
    try :

        find_over_time = overtime.query(Overtime).filter(Overtime.id == id).first()

        if(find_over_time == None):         
            return JSONResponse(status_code= 404, content="타임 데이터가 존재하지 않습니다.")
        
        find_over_time.manager_id = token.id
        find_over_time.proposer_note = schema.proposer_note
        find_over_time.processed_date = schema.processed_date
        find_over_time.application_status = schema.application_status

        
        return { "message" : "오버타임 데이터 업데이트에 성공하였습니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


# overtime 데이터 소프트 삭제 [어드민만]
@router.delete('/{id}')
async def time_soft_delete(id : int):
    try:
        find_over_time = overtime.query(Overtime).filter(Overtime.id == id).first()

        if(find_over_time == None):
            return JSONResponse(status_code= 404, content="타임 데이터가 존재하지 않습니다.")
        
        overtime.deleted_yn = "Y" 

        return { "message": "오버타임 데이터를 정상적으로 삭제하였습니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)

                                                                                                                                                                                                
# overtime 데이터 삭제 [어드민만]
@router.delete('/{id}')
async def time_delete(id : int):
    try:
        find_over_time = overtime.query(Overtime).filter(Overtime.id == id).first()

        if(find_over_time == None):
            return JSONResponse(status_code= 404, content="타임 데이터가 존재하지 않습니다.")
        
        overtime.delete(find_over_time)
        overtime.commit()  

        return { "message": "오버타임 데이터를 정상적으로 삭제하였습니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)


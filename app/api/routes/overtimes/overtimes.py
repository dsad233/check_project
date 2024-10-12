from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.models.models import Overtime
from fastapi.responses import JSONResponse


router = APIRouter(dependencies=[Depends(validate_token)])
overtime = async_session()


# overtime 전체 조회
@router.get("")
async def find_all():
    try:
        overtimeall = await overtime.query(Overtime).all()

        if(len(overtimeall) == 0):
            return JSONResponse(status_code= 404, content="타임 데이터가 존재하지 않습니다.")
        
        return { "message" : "타임 데이터 전체 조회에 성공하였습니다.", "data" : overtimeall }
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
async def time_create(schema : OverTimeCrete, token : Annotated[Users, Depends(vaildate_Token)]):
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
async def time_edit(id : int, schema : OverTimeEdit, token : Annotated[Users, Depends(vaildate_Token)]):
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


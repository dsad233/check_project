from fastapi import APIRouter
from app.api.core.database import Session
from app.api.models import Overtime
from fastapi.responses import JSONResponse

router = APIRouter()
overtime = Session()


# overtime 전체 조회
@router.get('/overtime')
async def findAll():
    try :
        overtimeall = overtime.query(Overtime).all()

        if(len(overtimeall) == 0):
            return JSONResponse(status_code= 404, content="타임 데이터가 존재하지 않습니다.")
        
        return { "message" : "타임 데이터 전체 조회에 성공하였습니다.", "data" : overtimeall }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
    

# overtime 상세 조회
@router.get('/overtime/{id}')
async def findOne():
    try :
        overtimeone = overtime.query(Overtime).filter(Overtime.manager_id == id).first()

        if(overtimeone == None):
            return JSONResponse(status_code= 404, content="타임 데이터가 존재하지 않습니다.")
        
        return { "message" : "타임 데이터 전체 조회에 성공하였습니다.", "data" : overtimeone }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
    


# overtime 생성
@router.get('/overtime/{id}')
async def findOne():
    try :


        
        return { "message" : "타임 데이터 전체 조회에 성공하였습니다." }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
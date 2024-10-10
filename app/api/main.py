from fastapi import FastAPI
from app.api.utils.DB.database import engine, Session
import uvicorn
from app.api.models import models

app = FastAPI()
db = Session()

models.Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
    print("서버가 열렸습니다.")
from fastapi import FastAPI
from app.api.core.database import engine, Session
import uvicorn
from app.api.models import models
from app.api import main

app = FastAPI()
db = Session()

models.Base.metadata.create_all(bind=engine)

app.include_router(main.app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
    print("서버가 열렸습니다.")
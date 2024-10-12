from fastapi import FastAPI

from app.api import main

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "hello wrold"}


app.include_router(main.app)

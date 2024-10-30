# src/main.py

from fastapi import FastAPI
from database import engine
from models import Base

app = FastAPI()

# 데이터베이스 생성
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to Daily Jam!"}
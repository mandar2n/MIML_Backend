from fastapi import FastAPI
#from src.config.config import load_config

# 환경 변수 및 설정 로드
#load_config()

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}
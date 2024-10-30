# src/config/settings.py

import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# DATABASE_URL 환경 변수를 불러옴
DATABASE_URL = os.getenv("DATABASE_URL")

# 로드된 값이 없는 경우를 대비해 오류를 방지하는 코드 추가 (선택적)
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment variables.")
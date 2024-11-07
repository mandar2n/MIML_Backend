import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from jose import JWTError
from src.auth.security import verify_password
from src.models import User
from src.config.config import load_config

ACCESS_TOKEN_EXPIRE_MINUTES = 30

config = load_config()
SECRET_KEY = config["SECRET_KEY"]
ALGORITHM = config["ALGORITHM"]

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

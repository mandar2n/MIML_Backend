# src/config/config.py


import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()  # .env 파일에서 환경 변수를 로드

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    SCHEDULER_CRON_HOUR = int(os.getenv("SCHEDULER_CRON_HOUR", 0))


    if not client_id or not client_secret:
        raise ValueError("Spotify Client ID or Secret is not set in the environment variables.")
    if not secret_key or not algorithm:
        raise ValueError("SECRET_KEY or ALGORITHM is not set in the environment variables.")

    return {
        "SPOTIFY_CLIENT_ID": client_id,
        "SPOTIFY_CLIENT_SECRET": client_secret,
        "SECRET_KEY": secret_key,
        "ALGORITHM": algorithm,
        "SCHEDULER_CRON_HOUR": SCHEDULER_CRON_HOUR
    }
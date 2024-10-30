# src/config/config.py

import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()  # .env 파일에서 환경 변수를 로드

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("Spotify Client ID or Secret is not set in the environment variables.")

    return {
        "SPOTIFY_CLIENT_ID": client_id,
        "SPOTIFY_CLIENT_SECRET": client_secret
    }
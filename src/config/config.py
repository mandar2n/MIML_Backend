import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()  # .env 파일에서 환경 변수를 로드

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")

    if not client_id or not client_secret:
        raise ValueError("Spotify Client ID or Secret is not set in the environment variables.")
    if not secret_key or not algorithm:
        raise ValueError("SECRET_KEY or ALGORITHM is not set in the environment variables.")

    return {
        "SPOTIFY_CLIENT_ID": client_id,
        "SPOTIFY_CLIENT_SECRET": client_secret,
        "SECRET_KEY": secret_key,
        "ALGORITHM": algorithm
    }
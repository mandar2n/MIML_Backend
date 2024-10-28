import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    os.getenv("SPOTIFY_CLIENT_ID")
    os.getenv("SPOTIFY_CLIENT_SECRET")

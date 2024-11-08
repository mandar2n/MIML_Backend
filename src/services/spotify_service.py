# src/services/spotify_service.py

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Optional, Dict
from src.config.config import load_config  # 새로운 파일 구조에 맞추어 import

# 환경 변수 로드
config = load_config()

# Spotify API 인증 설정
client_credentials_manager = SpotifyClientCredentials(
    client_id=config["SPOTIFY_CLIENT_ID"],
    client_secret=config["SPOTIFY_CLIENT_SECRET"]
)

spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_info(song_name: str) -> Optional[List[Dict[str, str]]]:
    """
    Spotify에서 검색된 모든 노래의 정보를 가져옵니다. 앨범 커버 이미지 URL과 URI 포함.
    """
    results = spotify.search(q=song_name, type="track", limit=40)  # 최대 40개의 결과 반환
    if results['tracks']['items']:
        song_list = []
        for track in results['tracks']['items']:
            # 앨범 커버 이미지 URL 추출
            album_images = track['album']['images']
            album_cover_url = album_images[0]['url'] if album_images else None

            song_info = {
                "title": track['name'],
                "artist": track['artists'][0]['name'],
                "album": track['album']['name'],
  
                "spotify_url": track['external_urls']['spotify'],
                "album_cover_url": album_cover_url,  # 앨범 커버 이미지 URL 추가
                "uri": track['uri']  # URI 추가
            }
            song_list.append(song_info)
        return song_list
    else:
        return None
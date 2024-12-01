# src/routers/songs.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.crud import share_song
from src.services.spotify_service import get_song_details
from src.schemas import SongShare,SongDetailResponse  # SongShare 스키마 추가 필요
from src.auth.dependencies import get_current_user
from src.models import User,Song
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

router = APIRouter()

@router.get("/{song_uri}", response_model=SongDetailResponse)
def get_song_detail(song_uri: str):
    """
    선택된 노래의 상세 정보를 반환하는 엔드포인트.
    """
    song_detail = get_song_details(song_uri)
    if not song_detail:
        raise HTTPException(status_code=404, detail="Song details not found")
    return song_detail


@router.post("/{song_uri}/share")
async def share_song_to_feed(
    song: SongShare, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 현재 사용자 정보 가져오기
):
    """
    사용자가 노래를 선택하여 피드에 공유하는 엔드포인트
    """
    # 현재 날짜를 가져옵니다.
    today = datetime.utcnow().date()

    stmt = select(Song).where(
        Song.sharedBy == current_user.userId,
        Song.sharedAt >= today
    )

    result = await db.execute(stmt)
    existing_share = result.scalars().first()
    
    if existing_share:
        raise HTTPException(
            status_code=400, 
            detail="You have already shared song today."
        )

    # 공유 로직 실행
    shared_song = await share_song(
        db=db,
        user_id=current_user.userId,  # current_user에서 user_id 가져오기
        song_title=song.title,
        artist=song.artist,
        album=song.album,
        spotify_url=song.spotify_url,   
        album_cover_url=song.album_cover_url,
        uri=song.uri
    )
    
    if not shared_song:
        raise HTTPException(status_code=400, detail="Failed to share song.")
    
    return {"message": "Song shared successfully", "shared_song": shared_song}

# 노래에 리액션 기능 엔드포인트
@router.post("/{song_id}/reactions")
async def add_reaction(
    song_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    
    # 노래 존재 여부 확인
    result = await db.execute(select(Song).filter(Song.songId == song_id))
    song = result.scalars().first()
    
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    # 리액션 수 증가
    song.reaction += 1
    
    # 세션에 변경 사항 반영
    db.add(song)  # 변경된 객체를 세션에 추가

    # 데이터베이스 커밋
    await db.commit()

    # 변경된 데이터를 다시 로드하여 반영
    await db.refresh(song)

    return {"message": "Reaction added successfully", "songId": song.songId, "reactions": song.reaction}

# 노래의 리액션 수 조회 기능 엔드포인트
@router.get("{song_id}/reactions")
async def get_reactions(
    song_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    
    # 노래 존재 여부 확인
    result = await db.execute(select(Song).filter(Song.songId == song_id))
    song = result.scalars().first()
    
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    return {"songId": song.songId, "reactions": song.reaction}
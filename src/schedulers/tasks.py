from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import delete
from datetime import datetime, timedelta
from src.database import get_db
from src.models import User, Song, Playlist, Follow, playlist_songs

async def recreate_daily_playlist(
    db: AsyncSession = Depends(get_db), 
    is_test: bool = False
) -> Optional[dict]:
    
    """
    오늘의 플레이리스트를 재생성하는 함수.
    - is_test=True: 디버깅 정보 반환 및 롤백 (테스트용)
    - is_test=False: 실제 데이터베이스에 커밋 (스케줄러용)
    """
    
    now = datetime.utcnow()
    past_24_hours = now - timedelta(hours=24)

    try:
        async with db.begin():
            
            # 디버깅: 현재 시간 출력
            print(f"Recreating playlists at {datetime.utcnow()}")
            
            # 모든 사용자 가져오기
            users_result = await db.execute(select(User))
            users = users_result.scalars().all()
            print(f"Total users: {len(users)}") # 디버깅
            
            processed_users = []
            created_playlists = []

            for user in users:
                print(f"Processing user: {user.email}") # 디버깅
                
                # 오늘의 플레이리스트 가져오기
                playlist_result = await db.execute(
                    select(Playlist).where(
                        Playlist.user_id == user.userId,
                        Playlist.playlist_type == "daily"
                    )
                )
                playlist = playlist_result.scalar_one_or_none()

                if not playlist:
                    # 오늘의 플레이리스트가 없으면 새로 생성
                    playlist = Playlist(
                        name="Today's Playlist",
                        playlist_type="daily",
                        createdAt=datetime.utcnow(),
                        user_id=user.userId
                    )
                    db.add(playlist)
                    await db.flush()  # playlistId 생성 후 사용
                    created_playlists.append(playlist.playlistId)

                # 팔로우한 사용자 ID 가져오기
                followed_user_ids_result = await db.execute(
                    select(Follow.following_id).where(Follow.follower_id == user.userId)
                )
                followed_user_ids = [row.following_id for row in followed_user_ids_result]

                # 지난 24시간 동안 공유된 노래 가져오기
                shared_songs_result = await db.execute(
                    select(Song).where(
                        Song.sharedAt >= past_24_hours,
                        Song.sharedBy.in_([user.userId] + followed_user_ids)
                    )
                )
                shared_songs = shared_songs_result.scalars().all()
                
                # 중복 제거: 제목과 가수를 기준으로
                unique_songs = {}
                for song in shared_songs:
                    key = (song.title.strip().lower(), song.artist.strip().lower())  # 대소문자 및 공백 제거
                    if key not in unique_songs:
                        unique_songs[key] = song


                # 기존 플레이리스트의 노래 삭제
                await db.execute(
                    delete(playlist_songs).where(playlist_songs.c.playlist_id == playlist.playlistId)
                )

                # 새로운 노래 추가
                if unique_songs:
                    for song in unique_songs.values():
                        await db.execute(
                            playlist_songs.insert().values(
                                playlist_id=playlist.playlistId,
                                song_id=song.songId
                            )
                        )
                else:
                    print(f"No songs shared in the last 24 hours for user {user.userId}. Playlist will be empty.")
                
                processed_users.append(user.userId)
                
        if is_test:
            # 테스트 환경에서는 디버깅 정보 반환
            return {
                "users": processed_users,
                "playlists": created_playlists,
                "shared_songs": len(shared_songs) if shared_songs else 0,
                "unique_songs": len(unique_songs) if unique_songs  else 0
            }

        # 실제 환경에서는 데이터베이스 커밋 후 로그 출력
        await db.commit()
        print(f"Recreated daily playlists successfully at {now}.")

    except Exception as e:
        print(f"Error in recreate_daily_playlist: {str(e)}")
        if is_test:
            raise  # 테스트 시 예외를 바로 반환
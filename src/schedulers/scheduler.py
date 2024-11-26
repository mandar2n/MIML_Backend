from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from schedulers.tasks import recreate_daily_playlist
from src.database import get_db
from fastapi import Depends

scheduler = AsyncIOScheduler()

def init_scheduler():
    scheduler.start()

    # 스케줄 작업 등록 (매일 특정 시간에 실행)
    scheduler.add_job(
        func=lambda: recreate_daily_playlist(next(get_db())),
        trigger=CronTrigger(hour=8),  # 매일 오전 8시 실행
        id="recreate_daily_playlist_job",
        replace_existing=True,
    )

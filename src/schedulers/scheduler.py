from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.database import get_db
from fastapi import Depends
from src.schedulers.tasks import recreate_daily_playlist
from pytz import timezone

scheduler = AsyncIOScheduler()

def init_scheduler():
    scheduler.start()

    # 스케줄 작업 등록 (매일 한국 시간 18시 실행)
    scheduler.add_job(
        func=lambda: recreate_daily_playlist(next(get_db())),
        trigger=CronTrigger(hour=18, timezone=timezone("Asia/Seoul")),  
        id="recreate_daily_playlist_job",
        replace_existing=True,
    )

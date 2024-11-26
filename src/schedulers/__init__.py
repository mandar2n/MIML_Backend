from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.schedulers.tasks import recreate_daily_playlist
from src.database import get_db

def init_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=recreate_daily_playlist,
        trigger="cron",
        hour=0,  # 매일 자정에 실행
        kwargs={"db": next(get_db())}
    )
    scheduler.start()

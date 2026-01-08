import logging

from app.tasks.reminder import send_session_reminders
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(
        send_session_reminders,
        trigger=IntervalTrigger(minutes=5),
        id="session_reminders",
        name="Send session reminders",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Background task scheduler started")


def shutdown_scheduler():
    scheduler.shutdown(wait=True)
    logger.info("Background task scheduler stopped")

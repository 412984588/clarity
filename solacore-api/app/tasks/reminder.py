import logging
from datetime import datetime, timezone

from app.database import AsyncSessionLocal
from app.models.solve_session import SolveSession
from app.services.email_service import send_session_reminder_email
from sqlalchemy import and_, select
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)


async def send_session_reminders():
    async with AsyncSessionLocal() as session:
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        stmt = (
            select(SolveSession)
            .options(joinedload(SolveSession.user))
            .where(
                and_(
                    SolveSession.reminder_time <= now,
                    ~SolveSession.reminder_sent,
                    SolveSession.reminder_time.isnot(None),
                )
            )
            .limit(100)
        )

        result = await session.execute(stmt)
        sessions_to_remind = result.scalars().all()

        if not sessions_to_remind:
            logger.info("No sessions requiring reminders")
            return

        logger.info(f"Found {len(sessions_to_remind)} sessions needing reminders")

        for solve_session in sessions_to_remind:
            try:
                await send_session_reminder_email(
                    user=solve_session.user, session=solve_session
                )

                solve_session.reminder_sent = True
                solve_session.reminder_sent_at = datetime.now(timezone.utc)

                logger.info(f"Sent reminder for session {solve_session.id}")

            except Exception as e:
                logger.error(
                    f"Failed to send reminder for session {solve_session.id}: {e}",
                    exc_info=True,
                )

        await session.commit()
        logger.info(f"Successfully processed {len(sessions_to_remind)} reminders")

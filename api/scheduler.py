from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from api.config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)
scheduler = None


def init_scheduler():
    """Initialize APScheduler with SQLite job store"""
    global scheduler
    
    jobstores = {
        'default': SQLAlchemyJobStore(url=DATABASE_URL)
    }
    
    scheduler = AsyncIOScheduler(jobstores=jobstores)
    scheduler.start()
    
    logger.info("Scheduler initialized")
    return scheduler


def get_scheduler():
    return scheduler


async def scheduled_generate_task():
    """Task to run on schedule"""
    from api.database import SessionLocal
    from api.repositories.settings_repository import SettingsRepository
    from api.repositories.job_repository import JobRepository
    from api.routers.generate import generate_video_task
    
    db = SessionLocal()
    try:
        settings_repo = SettingsRepository(db)
        job_repo = JobRepository(db)
        settings = settings_repo.get()
        
        if not settings.schedule_enabled:
            return
        
        # Create job
        job = job_repo.create(settings.videos_per_day)
        
        # Run generation
        await generate_video_task(job.id, settings.videos_per_day)
        
        logger.info(f"Scheduled generation completed: {settings.videos_per_day} videos")
        
    except Exception as e:
        logger.error(f"Scheduled generation failed: {e}")
    finally:
        db.close()


def update_schedule(schedule_time: str, enabled: bool):
    """Update the scheduled job"""
    global scheduler
    
    if not scheduler:
        return
    
    job_id = "scheduled_generate"
    
    # Remove existing job
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass
    
    if enabled:
        # Parse time (HH:MM format)
        hour, minute = schedule_time.split(":")
        
        # Add new job
        scheduler.add_job(
            scheduled_generate_task,
            CronTrigger(hour=int(hour), minute=int(minute)),
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Schedule updated: {schedule_time} daily")

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import asyncio

from api.database import get_db
from api.repositories.job_repository import JobRepository
from api.repositories.video_repository import VideoRepository
from api.repositories.settings_repository import SettingsRepository
from generator.quran_service import QuranService
from generator.video_generator import VideoGenerator
from generator.background_manager import BackgroundManager

router = APIRouter()

# Global job tracking
current_job_id = None


class GenerateRequest(BaseModel):
    count: int = 1


async def generate_video_task(job_id: str, count: int):
    """Background task to generate videos"""
    global current_job_id
    current_job_id = job_id
    
    from api.database import SessionLocal
    db = SessionLocal()
    
    try:
        job_repo = JobRepository(db)
        video_repo = VideoRepository(db)
        settings_repo = SettingsRepository(db)
        
        job_repo.update_status(job_id, "running")
        settings = settings_repo.get()
        
        quran_service = QuranService()
        video_generator = VideoGenerator()
        bg_manager = BackgroundManager()
        
        used_ayat = video_repo.get_used_ayat()
        
        for i in range(count):
            # Check if cancelled
            if current_job_id is None:
                break
                
            try:
                # Get random ayat
                surah, ayat = quran_service.get_random_ayat_reference(used_ayat)
                used_ayat.add((surah, ayat))
                
                # Fetch ayat data
                ayat_data = await quran_service.get_ayat(surah, ayat, settings.qari)
                
                # Get background (download from Pexels if none available)
                background = await bg_manager.get_or_download_background()
                if not background:
                    raise Exception("No background videos available and failed to download from Pexels")
                
                # Download audio
                import tempfile
                audio_path = tempfile.mktemp(suffix=".mp3")
                await quran_service.download_audio(ayat_data["audio_url"], audio_path)
                
                # Generate video
                result = await video_generator.generate_video(
                    background_path=background,
                    audio_path=audio_path,
                    text_arab=ayat_data["text_arab"],
                    text_translation=ayat_data["text_translation"],
                    surah_name=ayat_data["surah_name"],
                    ayat_number=ayat
                )
                
                # Save to database
                video_repo.create({
                    "surah": surah,
                    "ayat": ayat,
                    "surah_name": ayat_data["surah_name"],
                    "text_arab": ayat_data["text_arab"],
                    "text_translation": ayat_data["text_translation"],
                    "qari": settings.qari,
                    "background_file": background,
                    "output_file": result["output_file"],
                    "duration": result["duration"],
                    "file_size": result["file_size"],
                    "status": "completed"
                })
                
                job_repo.increment_completed(job_id)
                
            except Exception as e:
                job_repo.increment_failed(job_id)
                print(f"Error generating video: {e}")
        
        # Mark job as completed if not cancelled
        if current_job_id is not None:
            job_repo.update_status(job_id, "completed")
        
        await quran_service.close()
        
    except Exception as e:
        print(f"Job error: {e}")
        job_repo.update_status(job_id, "failed")
    finally:
        db.close()
        current_job_id = None


@router.post("")
async def generate_videos(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger video generation"""
    global current_job_id
    
    if current_job_id:
        raise HTTPException(status_code=400, detail="Generation already in progress")
    
    job_repo = JobRepository(db)
    job = job_repo.create(request.count)
    
    background_tasks.add_task(generate_video_task, job.id, request.count)
    
    return {"job_id": job.id, "count": request.count, "status": "queued"}


@router.get("/status")
async def get_generate_status(db: Session = Depends(get_db)):
    """Get current generation status"""
    job_repo = JobRepository(db)
    current_job = job_repo.get_current_job()
    
    if not current_job:
        return {"status": "idle", "current_job": None}
    
    return {
        "status": "running",
        "current_job": job_repo.to_dict(current_job)
    }


@router.post("/cancel")
async def cancel_generation(db: Session = Depends(get_db)):
    """Cancel current generation job"""
    global current_job_id
    
    job_repo = JobRepository(db)
    
    # Get current running job from DB
    current_job = job_repo.get_current_job()
    
    if current_job:
        job_repo.update_status(current_job.id, "cancelled")
    
    # Reset global state
    current_job_id = None
    
    return {"status": "cancelled"}


@router.post("/reset")
async def reset_generation(db: Session = Depends(get_db)):
    """Reset generation state (force clear stuck jobs)"""
    global current_job_id
    current_job_id = None
    
    return {"status": "reset"}

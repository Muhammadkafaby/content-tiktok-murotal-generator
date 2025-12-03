from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from api.models.job import GenerateJob


class JobRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, count: int) -> GenerateJob:
        """Create a new generate job"""
        job = GenerateJob(count=count, status="pending")
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def get_by_id(self, job_id: str) -> Optional[GenerateJob]:
        """Get job by ID"""
        return self.db.query(GenerateJob).filter(GenerateJob.id == job_id).first()
    
    def get_current_job(self) -> Optional[GenerateJob]:
        """Get currently running job"""
        return self.db.query(GenerateJob)\
            .filter(GenerateJob.status.in_(["pending", "running"]))\
            .first()
    
    def get_recent(self, limit: int = 10) -> List[GenerateJob]:
        """Get recent jobs"""
        return self.db.query(GenerateJob)\
            .order_by(desc(GenerateJob.started_at))\
            .limit(limit)\
            .all()
    
    def update_status(self, job_id: str, status: str) -> Optional[GenerateJob]:
        """Update job status"""
        job = self.get_by_id(job_id)
        if job:
            job.status = status
            if status == "running" and not job.started_at:
                job.started_at = datetime.utcnow()
            if status in ["completed", "cancelled"]:
                job.finished_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(job)
        return job
    
    def increment_completed(self, job_id: str) -> Optional[GenerateJob]:
        """Increment completed count"""
        job = self.get_by_id(job_id)
        if job:
            job.completed += 1
            if job.completed >= job.count:
                job.status = "completed"
                job.finished_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(job)
        return job
    
    def increment_failed(self, job_id: str) -> Optional[GenerateJob]:
        """Increment failed count"""
        job = self.get_by_id(job_id)
        if job:
            job.failed += 1
            self.db.commit()
            self.db.refresh(job)
        return job
    
    def to_dict(self, job: GenerateJob) -> dict:
        """Convert job to dictionary"""
        return {
            "id": job.id,
            "count": job.count,
            "completed": job.completed,
            "failed": job.failed,
            "status": job.status,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
            "progress": round(job.completed / job.count * 100, 1) if job.count > 0 else 0
        }

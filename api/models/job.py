from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from api.database import Base
import uuid


class GenerateJob(Base):
    __tablename__ = "generate_jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    count = Column(Integer, nullable=False)
    completed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, running, completed, cancelled
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

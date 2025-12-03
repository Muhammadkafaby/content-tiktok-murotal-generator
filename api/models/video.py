from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
from api.database import Base
import uuid


class Video(Base):
    __tablename__ = "videos"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    surah = Column(Integer, nullable=False)
    ayat = Column(Integer, nullable=False)
    surah_name = Column(String(100), nullable=False)
    text_arab = Column(Text, nullable=False)
    text_translation = Column(Text, nullable=False)
    qari = Column(String(50), nullable=False)
    background_file = Column(String(255), nullable=False)
    output_file = Column(String(255), nullable=False)
    duration = Column(Float, default=0)
    file_size = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, server_default=func.now())

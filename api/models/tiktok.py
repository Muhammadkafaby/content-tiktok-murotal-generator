from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from api.database import Base
import uuid


class TikTokSession(Base):
    __tablename__ = "tiktok_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cookies = Column(Text, nullable=True)  # Encrypted JSON
    username = Column(String(100), nullable=True)
    is_valid = Column(Boolean, default=False)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class PostHistory(Base):
    __tablename__ = "post_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False)
    tiktok_url = Column(String(500), nullable=True)
    caption = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, success, failed
    error_message = Column(Text, nullable=True)
    posted_at = Column(DateTime, server_default=func.now())

from sqlalchemy import Column, String, Integer, Boolean
from api.database import Base


class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, default=1)
    qari = Column(String(50), default="alafasy")
    schedule_enabled = Column(Boolean, default=False)
    schedule_time = Column(String(10), default="06:00")
    videos_per_day = Column(Integer, default=5)
    max_ayat_length = Column(Integer, default=500)
    
    # TikTok settings
    tiktok_auto_post = Column(Boolean, default=False)
    tiktok_post_delay = Column(Integer, default=60)
    tiktok_hashtags = Column(String(500), default="#quran #murotal #islamic #muslim #fyp")
    
    # AI Caption settings
    caption_mode = Column(String(20), default="template")  # template or ai

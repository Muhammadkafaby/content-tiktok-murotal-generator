from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from api.models.tiktok import TikTokSession, PostHistory


class TikTokRepository:
    def __init__(self, db: Session):
        self.db = db
    
    # TikTok Session methods
    def get_session(self) -> Optional[TikTokSession]:
        """Get current TikTok session"""
        return self.db.query(TikTokSession).first()
    
    def create_session(self, cookies: str, username: str) -> TikTokSession:
        """Create or update TikTok session"""
        session = self.get_session()
        if session:
            session.cookies = cookies
            session.username = username
            session.is_valid = True
            session.last_used = datetime.utcnow()
        else:
            session = TikTokSession(
                cookies=cookies,
                username=username,
                is_valid=True
            )
            self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def invalidate_session(self) -> None:
        """Mark session as invalid"""
        session = self.get_session()
        if session:
            session.is_valid = False
            self.db.commit()
    
    def update_last_used(self) -> None:
        """Update last used timestamp"""
        session = self.get_session()
        if session:
            session.last_used = datetime.utcnow()
            self.db.commit()
    
    # Post History methods
    def create_post(self, video_id: str, caption: str) -> PostHistory:
        """Create post history record"""
        post = PostHistory(
            video_id=video_id,
            caption=caption,
            status="pending"
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post
    
    def update_post_status(
        self,
        post_id: str,
        status: str,
        tiktok_url: str = None,
        error_message: str = None
    ) -> Optional[PostHistory]:
        """Update post status"""
        post = self.db.query(PostHistory).filter(PostHistory.id == post_id).first()
        if post:
            post.status = status
            if tiktok_url:
                post.tiktok_url = tiktok_url
            if error_message:
                post.error_message = error_message
            self.db.commit()
            self.db.refresh(post)
        return post
    
    def get_post_history(self, limit: int = 20) -> List[PostHistory]:
        """Get recent post history"""
        return self.db.query(PostHistory)\
            .order_by(desc(PostHistory.posted_at))\
            .limit(limit)\
            .all()
    
    def get_posts_by_video(self, video_id: str) -> List[PostHistory]:
        """Get posts for a specific video"""
        return self.db.query(PostHistory)\
            .filter(PostHistory.video_id == video_id)\
            .all()
    
    def count_successful_posts(self) -> int:
        """Count successful posts"""
        return self.db.query(PostHistory)\
            .filter(PostHistory.status == "success")\
            .count()

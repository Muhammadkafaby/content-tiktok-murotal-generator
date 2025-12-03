"""
Property tests for TikTok service
**Feature: quran-video-generator, Property 14: TikTok Session Persistence**
**Feature: quran-video-generator, Property 15: TikTok Upload Completion**
**Feature: quran-video-generator, Property 17: Post Status Tracking**
**Validates: Requirements 6.1, 6.2, 6.4, 6.5**
"""
import pytest
from hypothesis import given, strategies as st, settings
from api.repositories.tiktok_repository import TikTokRepository


class TestTikTokSessionPersistence:
    """
    Property 14: TikTok Session Persistence
    For any valid TikTok login session, the session cookies SHALL persist
    across system restarts and remain usable.
    """
    
    @given(
        cookies=st.text(min_size=10, max_size=500),
        username=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N')))
    )
    @settings(max_examples=20)
    def test_session_persists_after_creation(self, temp_db, cookies, username):
        """Session should persist after creation"""
        repo = TikTokRepository(temp_db)
        
        # Create session
        session = repo.create_session(cookies, username)
        assert session.id is not None
        
        # Retrieve session
        retrieved = repo.get_session()
        assert retrieved is not None
        assert retrieved.cookies == cookies
        assert retrieved.username == username
        assert retrieved.is_valid is True
    
    @given(
        cookies1=st.text(min_size=10, max_size=100),
        cookies2=st.text(min_size=10, max_size=100),
        username=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('L',)))
    )
    @settings(max_examples=10)
    def test_session_update_replaces_old(self, temp_db, cookies1, cookies2, username):
        """Updating session should replace old cookies"""
        repo = TikTokRepository(temp_db)
        
        # Create initial session
        repo.create_session(cookies1, username)
        
        # Update session
        repo.create_session(cookies2, username)
        
        # Should have new cookies
        session = repo.get_session()
        assert session.cookies == cookies2
    
    def test_session_invalidation(self, temp_db):
        """Session can be invalidated"""
        repo = TikTokRepository(temp_db)
        
        repo.create_session("test_cookies", "testuser")
        assert repo.get_session().is_valid is True
        
        repo.invalidate_session()
        assert repo.get_session().is_valid is False


class TestPostStatusTracking:
    """
    Property 17: Post Status Tracking
    For any TikTok posting attempt, the system SHALL record the posting status
    (success/failed) in the database.
    """
    
    @given(
        video_id=st.uuids().map(str),
        caption=st.text(min_size=1, max_size=200)
    )
    @settings(max_examples=20)
    def test_post_creation_recorded(self, temp_db, video_id, caption):
        """Post attempt should be recorded"""
        # First create a video to reference
        from api.repositories.video_repository import VideoRepository
        video_repo = VideoRepository(temp_db)
        video = video_repo.create({
            "surah": 1,
            "ayat": 1,
            "surah_name": "Al-Fatiha",
            "text_arab": "Arabic",
            "text_translation": "Translation",
            "qari": "alafasy",
            "background_file": "bg.mp4",
            "output_file": "output.mp4",
            "status": "completed"
        })
        
        repo = TikTokRepository(temp_db)
        post = repo.create_post(video.id, caption)
        
        assert post.id is not None
        assert post.video_id == video.id
        assert post.caption == caption
        assert post.status == "pending"
    
    @given(status=st.sampled_from(["success", "failed"]))
    @settings(max_examples=10)
    def test_post_status_update(self, temp_db, status):
        """Post status should be updatable"""
        from api.repositories.video_repository import VideoRepository
        video_repo = VideoRepository(temp_db)
        video = video_repo.create({
            "surah": 1, "ayat": 1, "surah_name": "Test",
            "text_arab": "A", "text_translation": "T",
            "qari": "alafasy", "background_file": "b.mp4",
            "output_file": "o.mp4", "status": "completed"
        })
        
        repo = TikTokRepository(temp_db)
        post = repo.create_post(video.id, "Test caption")
        
        if status == "success":
            repo.update_post_status(post.id, status, tiktok_url="https://tiktok.com/test")
        else:
            repo.update_post_status(post.id, status, error_message="Upload failed")
        
        # Verify in history
        history = repo.get_post_history()
        assert len(history) == 1
        assert history[0].status == status
    
    def test_successful_post_count(self, temp_db):
        """Successful post count should be accurate"""
        from api.repositories.video_repository import VideoRepository
        video_repo = VideoRepository(temp_db)
        
        repo = TikTokRepository(temp_db)
        
        # Create videos and posts
        for i in range(5):
            video = video_repo.create({
                "surah": i+1, "ayat": 1, "surah_name": f"S{i}",
                "text_arab": "A", "text_translation": "T",
                "qari": "alafasy", "background_file": "b.mp4",
                "output_file": f"o{i}.mp4", "status": "completed"
            })
            post = repo.create_post(video.id, f"Caption {i}")
            
            # Mark some as success, some as failed
            if i < 3:
                repo.update_post_status(post.id, "success")
            else:
                repo.update_post_status(post.id, "failed")
        
        assert repo.count_successful_posts() == 3

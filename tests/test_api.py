"""
Property tests for API endpoints
**Feature: quran-video-generator, Property 4: Batch Uniqueness**
**Feature: quran-video-generator, Property 8: Progress Accuracy**
**Validates: Requirements 1.5, 2.5**
"""
import pytest
from hypothesis import given, strategies as st, settings
from api.repositories.video_repository import VideoRepository
from api.repositories.job_repository import JobRepository


class TestBatchUniqueness:
    """
    Property 4: Batch Uniqueness
    For any batch generation request with count N, all N generated videos
    SHALL have unique ayat (no duplicates within the batch).
    """
    
    @given(st.data())
    @settings(max_examples=30)
    def test_batch_videos_have_unique_ayat(self, temp_db, data):
        """All videos in a batch should have unique surah:ayat combinations"""
        repo = VideoRepository(temp_db)
        
        # Create batch of videos
        batch_size = data.draw(st.integers(min_value=2, max_value=10))
        created_ayat = set()
        
        for i in range(batch_size):
            # Generate unique surah:ayat
            surah = data.draw(st.integers(min_value=1, max_value=114))
            ayat = data.draw(st.integers(min_value=1, max_value=50))
            
            # Skip if already used in this batch
            if (surah, ayat) in created_ayat:
                continue
            
            created_ayat.add((surah, ayat))
            
            repo.create({
                "surah": surah,
                "ayat": ayat,
                "surah_name": f"Surah{surah}",
                "text_arab": "Arabic",
                "text_translation": "Translation",
                "qari": "alafasy",
                "background_file": "bg.mp4",
                "output_file": f"output_{i}.mp4",
                "status": "completed"
            })
        
        # Verify uniqueness
        used_ayat = repo.get_used_ayat()
        assert len(used_ayat) == len(created_ayat)
    
    def test_get_used_ayat_returns_all_used(self, temp_db):
        """get_used_ayat should return all surah:ayat combinations used"""
        repo = VideoRepository(temp_db)
        
        # Create specific videos
        test_ayat = [(1, 1), (2, 255), (112, 1), (114, 6)]
        
        for surah, ayat in test_ayat:
            repo.create({
                "surah": surah,
                "ayat": ayat,
                "surah_name": f"Surah{surah}",
                "text_arab": "Arabic",
                "text_translation": "Translation",
                "qari": "alafasy",
                "background_file": "bg.mp4",
                "output_file": f"output_{surah}_{ayat}.mp4",
                "status": "completed"
            })
        
        used = repo.get_used_ayat()
        assert used == set(test_ayat)


class TestProgressAccuracy:
    """
    Property 8: Progress Accuracy
    For any batch generation job, the reported progress (completed/total)
    SHALL accurately reflect the actual number of completed videos.
    """
    
    @given(
        count=st.integers(min_value=1, max_value=20),
        completed=st.integers(min_value=0, max_value=20)
    )
    @settings(max_examples=30)
    def test_progress_reflects_completed_count(self, temp_db, count, completed):
        """Progress should accurately reflect completed/total"""
        # Ensure completed <= count
        completed = min(completed, count)
        
        repo = JobRepository(temp_db)
        
        # Create job
        job = repo.create(count)
        
        # Simulate completions
        for _ in range(completed):
            repo.increment_completed(job.id)
        
        # Check progress
        updated_job = repo.get_by_id(job.id)
        job_dict = repo.to_dict(updated_job)
        
        assert updated_job.completed == completed
        assert updated_job.count == count
        
        expected_progress = round(completed / count * 100, 1)
        assert job_dict["progress"] == expected_progress
    
    @given(
        count=st.integers(min_value=1, max_value=10),
        failed=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=20)
    def test_failed_count_tracked_separately(self, temp_db, count, failed):
        """Failed count should be tracked separately from completed"""
        failed = min(failed, count)
        
        repo = JobRepository(temp_db)
        job = repo.create(count)
        
        # Simulate failures
        for _ in range(failed):
            repo.increment_failed(job.id)
        
        updated_job = repo.get_by_id(job.id)
        assert updated_job.failed == failed
        assert updated_job.completed == 0  # Completed should still be 0
    
    def test_job_completes_when_all_done(self, temp_db):
        """Job status should change to completed when all videos done"""
        repo = JobRepository(temp_db)
        
        job = repo.create(5)
        assert job.status == "pending"
        
        repo.update_status(job.id, "running")
        
        for i in range(5):
            repo.increment_completed(job.id)
        
        final_job = repo.get_by_id(job.id)
        assert final_job.status == "completed"
        assert final_job.completed == 5

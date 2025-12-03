"""
Property tests for scheduler
**Feature: quran-video-generator, Property 11: Scheduler Execution**
**Feature: quran-video-generator, Property 12: Generation History Tracking**
**Validates: Requirements 5.1, 5.3**
"""
import pytest
from hypothesis import given, strategies as st, settings
from api.repositories.job_repository import JobRepository
from api.repositories.settings_repository import SettingsRepository


class TestSchedulerExecution:
    """
    Property 11: Scheduler Execution
    For any enabled schedule configuration, the system SHALL trigger
    video generation within acceptable time tolerance.
    """
    
    @given(
        hour=st.integers(min_value=0, max_value=23),
        minute=st.integers(min_value=0, max_value=59)
    )
    @settings(max_examples=20)
    def test_schedule_time_format_valid(self, temp_db, hour, minute):
        """Schedule time should be stored in valid HH:MM format"""
        repo = SettingsRepository(temp_db)
        
        schedule_time = f"{hour:02d}:{minute:02d}"
        updated = repo.update({"schedule_time": schedule_time})
        
        retrieved = repo.get()
        assert retrieved.schedule_time == schedule_time
        
        # Verify format
        parts = retrieved.schedule_time.split(":")
        assert len(parts) == 2
        assert 0 <= int(parts[0]) <= 23
        assert 0 <= int(parts[1]) <= 59
    
    @given(enabled=st.booleans())
    @settings(max_examples=10)
    def test_schedule_enabled_persists(self, temp_db, enabled):
        """Schedule enabled state should persist"""
        repo = SettingsRepository(temp_db)
        
        repo.update({"schedule_enabled": enabled})
        retrieved = repo.get()
        
        assert retrieved.schedule_enabled == enabled


class TestGenerationHistoryTracking:
    """
    Property 12: Generation History Tracking
    For any completed video generation (manual or scheduled),
    the system SHALL record the generation event in history.
    """
    
    @given(count=st.integers(min_value=1, max_value=10))
    @settings(max_examples=20)
    def test_job_creation_recorded(self, temp_db, count):
        """Every generation job should be recorded"""
        repo = JobRepository(temp_db)
        
        job = repo.create(count)
        
        # Should be retrievable
        retrieved = repo.get_by_id(job.id)
        assert retrieved is not None
        assert retrieved.count == count
    
    @given(st.data())
    @settings(max_examples=20)
    def test_job_history_ordered_by_time(self, temp_db, data):
        """Job history should be ordered by creation time"""
        repo = JobRepository(temp_db)
        
        # Create multiple jobs
        num_jobs = data.draw(st.integers(min_value=2, max_value=5))
        job_ids = []
        
        for i in range(num_jobs):
            job = repo.create(i + 1)
            job_ids.append(job.id)
        
        # Get recent jobs
        recent = repo.get_recent(limit=num_jobs)
        
        # Should be in reverse order (newest first)
        assert len(recent) == num_jobs
        for i, job in enumerate(recent):
            assert job.id == job_ids[-(i + 1)]
    
    def test_job_status_transitions_recorded(self, temp_db):
        """Job status transitions should be recorded"""
        repo = JobRepository(temp_db)
        
        job = repo.create(5)
        assert job.status == "pending"
        
        repo.update_status(job.id, "running")
        job = repo.get_by_id(job.id)
        assert job.status == "running"
        assert job.started_at is not None
        
        repo.update_status(job.id, "completed")
        job = repo.get_by_id(job.id)
        assert job.status == "completed"
        assert job.finished_at is not None

"""
Property tests for data persistence
**Feature: quran-video-generator, Property 9: Data Persistence**
**Validates: Requirements 4.3, 4.4**
"""
import pytest
from hypothesis import given, strategies as st, settings
from api.repositories.video_repository import VideoRepository
from api.repositories.settings_repository import SettingsRepository
from api.repositories.job_repository import JobRepository


# Strategies for generating test data
video_data_strategy = st.fixed_dictionaries({
    "surah": st.integers(min_value=1, max_value=114),
    "ayat": st.integers(min_value=1, max_value=286),
    "surah_name": st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L',))),
    "text_arab": st.text(min_size=1, max_size=500),
    "text_translation": st.text(min_size=1, max_size=500),
    "qari": st.sampled_from(["alafasy", "abdulbasit", "sudais", "husary", "minshawi"]),
    "background_file": st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    "output_file": st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    "duration": st.floats(min_value=1.0, max_value=300.0),
    "file_size": st.integers(min_value=1000, max_value=100000000),
    "status": st.sampled_from(["pending", "processing", "completed", "failed"])
})


@given(video_data=video_data_strategy)
@settings(max_examples=50)
def test_video_persistence_roundtrip(temp_db, video_data):
    """
    Property 9: Data Persistence
    For any video saved to storage, the video metadata SHALL persist and be retrievable.
    """
    repo = VideoRepository(temp_db)
    
    # Create video
    created = repo.create(video_data)
    assert created.id is not None
    
    # Retrieve video
    retrieved = repo.get_by_id(created.id)
    assert retrieved is not None
    
    # Verify all fields match
    assert retrieved.surah == video_data["surah"]
    assert retrieved.ayat == video_data["ayat"]
    assert retrieved.surah_name == video_data["surah_name"]
    assert retrieved.text_arab == video_data["text_arab"]
    assert retrieved.text_translation == video_data["text_translation"]
    assert retrieved.qari == video_data["qari"]
    assert retrieved.status == video_data["status"]


@given(count=st.integers(min_value=1, max_value=20))
@settings(max_examples=20)
def test_job_persistence_roundtrip(temp_db, count):
    """
    Property 9: Data Persistence
    For any job saved to storage, the job metadata SHALL persist and be retrievable.
    """
    repo = JobRepository(temp_db)
    
    # Create job
    created = repo.create(count)
    assert created.id is not None
    assert created.count == count
    assert created.status == "pending"
    
    # Retrieve job
    retrieved = repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.count == count


@given(
    qari=st.sampled_from(["alafasy", "abdulbasit", "sudais"]),
    videos_per_day=st.integers(min_value=1, max_value=50),
    schedule_enabled=st.booleans()
)
@settings(max_examples=20)
def test_settings_persistence_roundtrip(temp_db, qari, videos_per_day, schedule_enabled):
    """
    Property 9: Data Persistence
    For any settings saved, the settings SHALL persist and be retrievable.
    """
    repo = SettingsRepository(temp_db)
    
    # Update settings
    updated = repo.update({
        "qari": qari,
        "videos_per_day": videos_per_day,
        "schedule_enabled": schedule_enabled
    })
    
    # Retrieve settings
    retrieved = repo.get()
    assert retrieved.qari == qari
    assert retrieved.videos_per_day == videos_per_day
    assert retrieved.schedule_enabled == schedule_enabled


def test_video_count_consistency(temp_db):
    """
    Property 9: Data Persistence
    Video count SHALL accurately reflect the number of stored videos.
    """
    repo = VideoRepository(temp_db)
    
    # Create multiple videos
    for i in range(5):
        repo.create({
            "surah": i + 1,
            "ayat": 1,
            "surah_name": f"Surah{i}",
            "text_arab": "Arabic text",
            "text_translation": "Translation",
            "qari": "alafasy",
            "background_file": "bg.mp4",
            "output_file": f"output{i}.mp4",
            "status": "completed"
        })
    
    assert repo.count() == 5
    
    # Delete one
    videos, _ = repo.get_all()
    repo.delete(videos[0].id)
    
    assert repo.count() == 4

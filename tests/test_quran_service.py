"""
Property tests for Quran API integration
**Feature: quran-video-generator, Property 1: Valid Ayat Selection**
**Feature: quran-video-generator, Property 2: Complete Data Retrieval**
**Validates: Requirements 1.1, 1.2**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from generator.quran_service import QuranService, AYAT_PER_SURAH, TOTAL_AYAT


# Valid surah:ayat strategy
def valid_ayat_strategy():
    """Generate valid surah:ayat combinations"""
    return st.integers(min_value=1, max_value=114).flatmap(
        lambda surah: st.tuples(
            st.just(surah),
            st.integers(min_value=1, max_value=AYAT_PER_SURAH[surah - 1])
        )
    )


class TestValidAyatSelection:
    """
    Property 1: Valid Ayat Selection
    For any generated video, the selected ayat SHALL be within valid range
    (surah 1-114, ayat within surah bounds) and exist in Al-Quran.
    """
    
    @given(surah=st.integers(min_value=1, max_value=114))
    @settings(max_examples=50)
    def test_valid_surah_range(self, surah):
        """All surah numbers 1-114 should be valid"""
        service = QuranService()
        # Any ayat 1 should be valid for any surah
        assert service.is_valid_ayat(surah, 1) is True
    
    @given(surah=st.integers(min_value=1, max_value=114))
    @settings(max_examples=50)
    def test_ayat_bounds_per_surah(self, surah):
        """Ayat should be within bounds for each surah"""
        service = QuranService()
        max_ayat = AYAT_PER_SURAH[surah - 1]
        
        # Valid: first and last ayat
        assert service.is_valid_ayat(surah, 1) is True
        assert service.is_valid_ayat(surah, max_ayat) is True
        
        # Invalid: beyond max
        assert service.is_valid_ayat(surah, max_ayat + 1) is False
    
    @given(surah=st.integers(max_value=0))
    @settings(max_examples=20)
    def test_invalid_surah_below_range(self, surah):
        """Surah below 1 should be invalid"""
        service = QuranService()
        assert service.is_valid_ayat(surah, 1) is False
    
    @given(surah=st.integers(min_value=115))
    @settings(max_examples=20)
    def test_invalid_surah_above_range(self, surah):
        """Surah above 114 should be invalid"""
        service = QuranService()
        assert service.is_valid_ayat(surah, 1) is False
    
    @given(ayat=st.integers(max_value=0))
    @settings(max_examples=20)
    def test_invalid_ayat_below_range(self, ayat):
        """Ayat below 1 should be invalid"""
        service = QuranService()
        assert service.is_valid_ayat(1, ayat) is False


class TestRandomAyatSelection:
    """
    Property 1: Valid Ayat Selection
    Random selection should always produce valid ayat.
    """
    
    @given(st.data())
    @settings(max_examples=100)
    def test_random_selection_always_valid(self, data):
        """Random ayat selection should always return valid surah:ayat"""
        service = QuranService()
        
        # Generate some used ayat
        used = set()
        num_used = data.draw(st.integers(min_value=0, max_value=100))
        for _ in range(num_used):
            surah = data.draw(st.integers(min_value=1, max_value=114))
            ayat = data.draw(st.integers(min_value=1, max_value=AYAT_PER_SURAH[surah - 1]))
            used.add((surah, ayat))
        
        # Get random ayat
        surah, ayat = service.get_random_ayat_reference(used)
        
        # Should be valid
        assert service.is_valid_ayat(surah, ayat) is True
        # Should not be in used set
        assert (surah, ayat) not in used
    
    @given(st.data())
    @settings(max_examples=50)
    def test_random_selection_no_duplicates_in_batch(self, data):
        """
        Property 4: Batch Uniqueness
        Batch generation should not produce duplicate ayat.
        """
        service = QuranService()
        batch_size = data.draw(st.integers(min_value=1, max_value=20))
        
        selected = set()
        for _ in range(batch_size):
            surah, ayat = service.get_random_ayat_reference(selected)
            # Should not be duplicate
            assert (surah, ayat) not in selected
            selected.add((surah, ayat))
        
        # All should be unique
        assert len(selected) == batch_size


class TestTotalAyatCount:
    """Verify total ayat count is correct"""
    
    def test_total_ayat_is_6236(self):
        """Total ayat in Quran should be 6236"""
        assert TOTAL_AYAT == 6236
    
    def test_surah_count_is_114(self):
        """Total surah count should be 114"""
        assert len(AYAT_PER_SURAH) == 114
    
    def test_al_fatiha_has_7_ayat(self):
        """Al-Fatiha (surah 1) should have 7 ayat"""
        assert AYAT_PER_SURAH[0] == 7
    
    def test_al_baqarah_has_286_ayat(self):
        """Al-Baqarah (surah 2) should have 286 ayat"""
        assert AYAT_PER_SURAH[1] == 286
    
    def test_an_nas_has_6_ayat(self):
        """An-Nas (surah 114) should have 6 ayat"""
        assert AYAT_PER_SURAH[113] == 6

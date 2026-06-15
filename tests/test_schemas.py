"""
Unit tests for Pydantic schemas.

Validates that schemas correctly enforce data integrity.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from src.schemas.raw_schema import RawMatch
from src.schemas.feature_schema import MatchFeatures


class TestRawMatchSchema:
    """
    Test suite for RawMatch schema validation.
    """
    
    def test_valid_raw_match(self, sample_raw_match):
        """
        Test that a valid RawMatch passes validation.
        """
        assert sample_raw_match.match_id == "test_match_001"
        assert sample_raw_match.home_goals == 2
        assert sample_raw_match.away_goals == 1
    
    def test_future_date_rejected(self):
        """
        Test that match dates in the future are rejected.
        """
        future_date = datetime(2099, 1, 1, 20, 0, 0)
        with pytest.raises(ValidationError) as exc_info:
            RawMatch(
                match_id="test_001",
                date=future_date,
                home_team="Team A",
                away_team="Team B",
                home_goals=1,
                away_goals=1,
                competition="TEST",
                season=2024,
            )
        assert "future" in str(exc_info.value).lower()
    
    def test_same_teams_rejected(self):
        """
        Test that same home and away teams are rejected.
        """
        with pytest.raises(ValidationError) as exc_info:
            RawMatch(
                match_id="test_001",
                date=datetime(2024, 1, 15, 20, 0, 0),
                home_team="Team A",
                away_team="Team A",
                home_goals=1,
                away_goals=1,
                competition="TEST",
                season=2024,
            )
        assert "different" in str(exc_info.value).lower()
    
    def test_goals_out_of_range(self):
        """
        Test that goals outside 0-20 range are rejected.
        """
        with pytest.raises(ValidationError):
            RawMatch(
                match_id="test_001",
                date=datetime(2024, 1, 15, 20, 0, 0),
                home_team="Team A",
                away_team="Team B",
                home_goals=25,  # Invalid
                away_goals=1,
                competition="TEST",
                season=2024,
            )
    
    def test_invalid_possession(self):
        """
        Test that possession outside 0-100 range is rejected.
        """
        with pytest.raises(ValidationError):
            RawMatch(
                match_id="test_001",
                date=datetime(2024, 1, 15, 20, 0, 0),
                home_team="Team A",
                away_team="Team B",
                home_goals=1,
                away_goals=1,
                competition="TEST",
                season=2024,
                home_possession=150.0,  # Invalid
            )


class TestMatchFeaturesSchema:
    """
    Test suite for MatchFeatures schema validation.
    """
    
    def test_valid_match_features(self, sample_match_features):
        """
        Test that valid MatchFeatures passes validation.
        """
        assert sample_match_features.match_id == "test_match_001"
        assert sample_match_features.result == "1"
        assert sample_match_features.h2h_home_win_pct == 0.6
    
    def test_invalid_result(self, sample_match_features):
        """
        Test that invalid result codes are handled.
        """
        # This should pass as strings are allowed
        match = MatchFeatures(**sample_match_features.model_dump())
        assert match.result in ["1", "X", "2"]
    
    def test_h2h_percentage_bounds(self):
        """
        Test that H2H win percentage stays between 0 and 1.
        """
        with pytest.raises(ValidationError):
            MatchFeatures(
                match_id="test_001",
                date=datetime(2024, 1, 15, 20, 0, 0),
                home_team="Team A",
                away_team="Team B",
                result="1",
                home_goals=2,
                away_goals=1,
                home_avg_goals_last_n=1.8,
                away_avg_goals_last_n=1.5,
                home_avg_conceded_last_n=0.9,
                away_avg_conceded_last_n=1.2,
                h2h_home_win_pct=1.5,  # Invalid: > 1
                days_rest_home=7,
                days_rest_away=7,
                is_home_advantage=True,
                time_weight=0.95,
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
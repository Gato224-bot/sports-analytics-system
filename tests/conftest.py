"""
Pytest configuration and shared fixtures.

Defines fixtures used across all tests.
"""

import pytest
from datetime import datetime
from src.schemas.raw_schema import RawMatch
from src.schemas.feature_schema import MatchFeatures


@pytest.fixture
def sample_raw_match() -> RawMatch:
    """
    Fixture providing a valid sample RawMatch for testing.
    """
    return RawMatch(
        match_id="test_match_001",
        date=datetime(2024, 1, 15, 20, 0, 0),
        home_team="Team A",
        away_team="Team B",
        home_goals=2,
        away_goals=1,
        competition="TEST",
        season=2024,
        home_possession=55.5,
        away_possession=44.5,
        home_shots=12,
        away_shots=8,
    )


@pytest.fixture
def sample_match_features() -> MatchFeatures:
    """
    Fixture providing a valid sample MatchFeatures for testing.
    """
    return MatchFeatures(
        match_id="test_match_001",
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
        h2h_home_win_pct=0.6,
        days_rest_home=7,
        days_rest_away=7,
        is_home_advantage=True,
        time_weight=0.95,
        home_possession=55.5,
        away_possession=44.5,
        home_shots=12,
        away_shots=8,
    )
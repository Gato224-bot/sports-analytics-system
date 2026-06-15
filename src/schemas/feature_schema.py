"""
Pydantic schemas for engineered features.

Defines the structure for feature-engineered data ready for modeling.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MatchFeatures(BaseModel):
    """
    Schema for a match with all engineered features.
    
    This represents the final data structure used for modeling.
    
    Attributes:
        match_id: Unique match identifier
        date: Match date
        home_team: Home team name
        away_team: Away team name
        result: Match result (1=home win, X=draw, 2=away win)
        home_goals: Home team goals
        away_goals: Away team goals
        home_avg_goals_last_n: Home team average goals in last N matches
        away_avg_goals_last_n: Away team average goals in last N matches
        home_avg_conceded_last_n: Home team avg goals conceded in last N
        away_avg_conceded_last_n: Away team avg goals conceded in last N
        h2h_home_win_pct: Home team win % in head-to-head matchups
        days_rest_home: Days of rest before match (home team)
        days_rest_away: Days of rest before match (away team)
        is_home_advantage: Dummy variable for home advantage
        time_weight: Temporal decay weight (recent = higher)
        home_possession: Home team possession percentage
        away_possession: Away team possession percentage
    """
    
    match_id: str
    date: datetime
    home_team: str
    away_team: str
    result: str = Field(..., description="Match result: '1' (home), 'X' (draw), '2' (away)")
    home_goals: int
    away_goals: int
    
    # Rolling statistics
    home_avg_goals_last_n: float = Field(..., ge=0)
    away_avg_goals_last_n: float = Field(..., ge=0)
    home_avg_conceded_last_n: float = Field(..., ge=0)
    away_avg_conceded_last_n: float = Field(..., ge=0)
    
    # Head-to-head
    h2h_home_win_pct: float = Field(..., ge=0, le=1)
    
    # Rest
    days_rest_home: int = Field(..., ge=0)
    days_rest_away: int = Field(..., ge=0)
    
    # Context
    is_home_advantage: bool = True  # Always true for home team
    
    # Temporal
    time_weight: float = Field(..., ge=0, le=1, description="Temporal decay weight")
    
    # Optional stats
    home_possession: Optional[float] = Field(None, ge=0, le=100)
    away_possession: Optional[float] = Field(None, ge=0, le=100)
    home_shots: Optional[int] = Field(None, ge=0)
    away_shots: Optional[int] = Field(None, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "match_id": "m_2024_01_001",
                "date": "2024-01-15T20:00:00Z",
                "home_team": "Manchester United",
                "away_team": "Liverpool",
                "result": "1",
                "home_goals": 2,
                "away_goals": 1,
                "home_avg_goals_last_n": 1.8,
                "away_avg_goals_last_n": 1.5,
                "home_avg_conceded_last_n": 0.9,
                "away_avg_conceded_last_n": 1.2,
                "h2h_home_win_pct": 0.6,
                "days_rest_home": 7,
                "days_rest_away": 7,
                "is_home_advantage": True,
                "time_weight": 0.95,
                "home_possession": 55.5,
                "away_possession": 44.5,
                "home_shots": 12,
                "away_shots": 8
            }
        }
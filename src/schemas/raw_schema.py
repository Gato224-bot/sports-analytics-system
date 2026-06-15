"""
Pydantic schemas for raw data validation.

Defines the structure and constraints for raw match data from APIs.
Acts as the first data quality gate.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger(__name__)


class RawMatch(BaseModel):
    """
    Schema for a raw match (partido) without any processing.
    
    Validation ensures data integrity at the point of entry.
    
    Attributes:
        match_id: Unique identifier for the match
        date: Match date and time (UTC)
        home_team: Home team name
        away_team: Away team name
        home_goals: Goals scored by home team (0-20)
        away_goals: Goals scored by away team (0-20)
        competition: League or tournament code (e.g., 'PL', 'LA_LIGA')
        season: Season year (e.g., 2023)
        home_possession: Optional possession percentage (0-100)
        away_possession: Optional possession percentage (0-100)
        home_shots: Optional shots taken by home team
        away_shots: Optional shots taken by away team
    """
    
    match_id: str = Field(..., min_length=1, description="Unique match identifier")
    date: datetime = Field(..., description="Match date and time (UTC)")
    home_team: str = Field(..., min_length=1, description="Home team name")
    away_team: str = Field(..., min_length=1, description="Away team name")
    home_goals: int = Field(..., ge=0, le=20, description="Home team goals")
    away_goals: int = Field(..., ge=0, le=20, description="Away team goals")
    competition: str = Field(..., min_length=1, description="Competition code")
    season: int = Field(..., ge=2000, le=2100, description="Season year")
    
    # Optional enrichment fields
    home_possession: Optional[float] = Field(None, ge=0, le=100)
    away_possession: Optional[float] = Field(None, ge=0, le=100)
    home_shots: Optional[int] = Field(None, ge=0)
    away_shots: Optional[int] = Field(None, ge=0)
    
    @field_validator('date')
    @classmethod
    def date_not_future(cls, v: datetime) -> datetime:
        """
        Validate that match date is not in the future.
        """
        if v > datetime.utcnow():
            raise ValueError("Match date cannot be in the future")
        return v
    
    @field_validator('away_team')
    @classmethod
    def teams_must_be_different(cls, v: str, info) -> str:
        """
        Validate that home and away teams are different.
        """
        if 'home_team' in info.data and v == info.data['home_team']:
            raise ValueError("Home and away teams must be different")
        return v
    
    @field_validator('home_possession', 'away_possession')
    @classmethod
    def possession_sum_valid(cls, v: Optional[float]) -> Optional[float]:
        """
        Possession values must sum to ~100% if both provided.
        """
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Possession must be between 0 and 100")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "match_id": "m_2024_01_001",
                "date": "2024-01-15T20:00:00Z",
                "home_team": "Manchester United",
                "away_team": "Liverpool",
                "home_goals": 2,
                "away_goals": 1,
                "competition": "PL",
                "season": 2024,
                "home_possession": 55.5,
                "away_possession": 44.5,
                "home_shots": 12,
                "away_shots": 8
            }
        }


class RawMatchBatch(BaseModel):
    """
    Schema for validating a batch of matches.
    """
    
    matches: list[RawMatch] = Field(..., min_items=1)
    source: str = Field(..., description="Data source (e.g., 'api_football_data')")
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "matches": [],  # Array of RawMatch objects
                "source": "api_football_data",
                "fetched_at": "2024-01-15T21:30:00Z"
            }
        }
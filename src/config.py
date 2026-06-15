"""
Global configuration and environment variables.

Handles database connections, API keys, and application settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """
    Application settings with type validation.
    
    All configuration is loaded from environment variables or .env file.
    """
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/sports_analytics"
    )
    database_echo: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"
    
    # API Keys
    football_data_api_key: Optional[str] = os.getenv("FOOTBALL_DATA_API_KEY")
    
    # Paths
    project_root: Path = Path(__file__).parent.parent
    data_raw_dir: Path = project_root / "data" / "raw"
    data_processed_dir: Path = project_root / "data" / "processed"
    data_features_dir: Path = project_root / "data" / "features"
    models_dir: Path = project_root / "models"
    notebooks_dir: Path = project_root / "notebooks"
    
    # MLflow
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
    mlflow_experiment_name: str = os.getenv("MLFLOW_EXPERIMENT_NAME", "sports_analytics")
    
    # Model Parameters
    random_seed: int = 42
    test_size: float = 0.2
    validation_size: float = 0.1
    
    # Feature Engineering
    rolling_window: int = 10  # Default window for rolling averages
    h2h_lookback: int = 5    # Head-to-head lookback matches
    time_decay_rate: float = 0.95  # Decay rate for temporal weighting
    
    # Data Quality
    outlier_iqr_multiplier: float = 1.5
    missing_value_threshold: float = 0.5  # Max % missing before dropping column
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def create_directories(self) -> None:
        """
        Create required data and models directories if they don't exist.
        """
        for directory in [
            self.data_raw_dir,
            self.data_processed_dir,
            self.data_features_dir,
            self.models_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.create_directories()
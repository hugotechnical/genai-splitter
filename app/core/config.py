from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GEN AI SPLITTER"
    
    # Logic Configs
    LINES_THRESHOLD: int = 20
    MIN_CONTENT_LENGTH: int = 15
    PAGE_BREAK_DELIMITER: str = '--- Page Break ---'
    FUZZY_THRESHOLD: int = 90
    MAX_KEYWORD_POSITION: int = 4
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_INPUT_DIR: Path = BASE_DIR / "data_input"
    DATA_OUTPUT_DIR: Path = BASE_DIR / "data_output" / "results"
    
    class Config:
        case_sensitive = True

settings = Settings()

# Ensure dirs exist
settings.DATA_INPUT_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
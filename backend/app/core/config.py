from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Get the path to the backend directory (backend/app/core/config.py -> 3 levels up)
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Musicology Research Assistant"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/musicology.db")
    
    # Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/uploads")
    PROCESSED_DIR: str = os.getenv("PROCESSED_DIR", "data/processed")
    TIMELINE_DIR: str = os.getenv("TIMELINE_DIR", "data/timelines")
    
    # OCR
    TESSERACT_PATH: str = os.getenv("TESSERACT_PATH", "tesseract")
    
    # NLP Settings
    SPACY_MODEL: str = os.getenv("SPACY_MODEL", "en_core_web_sm")
    
    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MAIN_MODEL: str = os.getenv("OPENROUTER_MAIN_MODEL", "moonshotai/kimi-k2.5")
    OPENROUTER_FALLBACK_MODEL: str = os.getenv("OPENROUTER_FALLBACK_MODEL", "openai/gpt-oss-120b")
    
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
for directory in [settings.UPLOAD_DIR, settings.PROCESSED_DIR, settings.TIMELINE_DIR]:
    os.makedirs(directory, exist_ok=True)

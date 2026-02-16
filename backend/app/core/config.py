import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

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
    
    # NLP Models
    SPACY_MODEL: str = os.getenv("SPACY_MODEL", "en_core_web_sm")
    SUMMARIZATION_MODEL: str = os.getenv("SUMMARIZATION_MODEL", "facebook/bart-large-cnn")
    NER_MODEL: str = os.getenv("NER_MODEL", "dslim/bert-base-NER")
    ZERO_SHOT_MODEL: str = os.getenv("ZERO_SHOT_MODEL", "facebook/bart-large-mnli")
    
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
for directory in [settings.UPLOAD_DIR, settings.PROCESSED_DIR, settings.TIMELINE_DIR]:
    os.makedirs(directory, exist_ok=True)

import os
from typing import List
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    MAX_TOKENS_PER_REQUEST: int = int(os.getenv("MAX_TOKENS_PER_REQUEST", "8000"))
    
    # File Upload Settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [".docx"]
    
    # Directory Configuration
    BASE_DIR = Path(__file__).parent
    UPLOAD_DIR = BASE_DIR / "uploads"
    OUTPUT_DIR = BASE_DIR / "outputs"
    DATA_DIR = BASE_DIR / "data"
    
    # ChromaDB Settings
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    ADGM_KNOWLEDGE_PATH: str = "data/adgm_knowledge"
    
    # Processing Settings
    MAX_CONCURRENT_ANALYSES: int = int(os.getenv("MAX_CONCURRENT_ANALYSES", "5"))
    
    # ADGM Document Types Configuration
    ADGM_DOCUMENT_TYPES = {
        "memorandum": {
            "name": "Memorandum of Association",
            "required_sections": [
                "Company Name", 
                "Registered Office", 
                "Objects", 
                "Share Capital", 
                "Liability of Members", 
                "Subscriber Details"
            ]
        },
        "articles": {
            "name": "Articles of Association",
            "required_sections": [
                "Share Classes and Rights", 
                "Board of Directors", 
                "General Meetings",
                "Dividend Policy", 
                "Transfer of Shares", 
                "Accounts and Audit"
            ]
        },
        "application": {
            "name": "Company Registration Application",
            "required_sections": [
                "Company Details", 
                "Business Activities", 
                "Directors Information",
                "Shareholders Information", 
                "Financial Projections"
            ]
        },
        "board_resolution": {
            "name": "Board Resolution",
            "required_sections": [
                "Meeting Details", 
                "Attendees", 
                "Resolutions",
                "Voting Record", 
                "Signatures"
            ]
        }
    }
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_CONFIG = {
        "web_scraping": {
            "enabled": True,
            "timeout": 30,
            "rate_limit_delay": 1  # seconds between requests
        },
        "pdf_processing": {
            "enabled": True,
            "max_size_mb": 50
        },
        "docx_processing": {
            "enabled": True,
            "max_size_mb": 20
        },
        "chunk_size": 1000,
        "chunk_overlap": 200
    }
    
    # Red Flag Patterns
    RED_FLAG_PATTERNS = [
        "unlawful activities",
        "money laundering",
        "terrorist financing", 
        "regulatory violations",
        "sanctions violations",
        "prohibited activities",
        "inadequate capital",
        "missing signatures",
        "incomplete information",
        "inconsistent dates",
        "unauthorized activities"
    ]
    
    @classmethod
    def ensure_directories_exist(cls):
        """Ensure all required directories exist"""
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.DATA_DIR.mkdir(exist_ok=True)

# Create settings instance and ensure directories exist
settings = Settings()
settings.ensure_directories_exist()
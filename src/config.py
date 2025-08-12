"""Configuration settings for ADGM Corporate Agent."""

import os
from typing import Dict, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    
    # Model settings
    default_llm_provider: str = Field(default="gemini", env="LLM_PROVIDER")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    gemini_model: str = Field(default="gemini-2.5-pro", env="GEMINI_MODEL")
    
    # Vector database settings
    vector_db_path: str = Field(default="./data/vector_db", env="VECTOR_DB_PATH")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    
    # Document processing
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    supported_formats: List[str] = Field(default=["docx"], env="SUPPORTED_FORMATS")
    
    # ADGM specific settings
    adgm_base_url: str = Field(default="https://www.adgm.com", env="ADGM_BASE_URL")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"  # Ignore extra fields instead of raising errors
    }


# ADGM Document Types and Categories
ADGM_DOCUMENT_TYPES = {
    "company_formation": [
        "Articles of Association",
        "Incorporation Application Form", 
        "Memorandum of Association",
        "UBO Declaration Form",
        "Board Resolution Templates",
        "Register of Members and Directors",
        "Shareholder Resolution Templates",
        "Change of Registered Address Notice"
    ],
    "licensing": [
        "License Application",
        "Business Plan",
        "Financial Projections",
        "Compliance Manual"
    ],
    "employment": [
        "Employment Contract",
        "Employee Handbook",
        "HR Policies"
    ],
    "commercial": [
        "Commercial Agreements",
        "Service Agreements",
        "Partnership Agreements"
    ],
    "compliance": [
        "Compliance Policies",
        "Risk Management Policies",
        "Data Protection Policies"
    ]
}

# Required documents for different processes
ADGM_PROCESS_REQUIREMENTS = {
    "Company Incorporation": [
        "Articles of Association",
        "Memorandum of Association", 
        "UBO Declaration Form",
        "Register of Members and Directors",
        "Board Resolution Templates"
    ],
    "License Application": [
        "License Application Form",
        "Business Plan",
        "Financial Projections",
        "Compliance Manual"
    ]
}

# Red flag patterns and rules
RED_FLAG_PATTERNS = {
    "jurisdiction_issues": [
        "UAE Federal Courts",
        "Dubai Courts",
        "Abu Dhabi Courts"
    ],
    "missing_clauses": [
        "governing law",
        "dispute resolution",
        "jurisdiction clause"
    ],
    "formatting_issues": [
        "missing signatures",
        "incomplete dates",
        "missing company seal"
    ]
}

# ADGM official links for reference
ADGM_REFERENCE_LINKS = [
    "https://www.adgm.com/registration-authority/registration-and-incorporation",
    "https://www.adgm.com/setting-up",
    "https://www.adgm.com/legal-framework/guidance-and-policy-statements",
    "https://www.adgm.com/operating-in-adgm/obligations-of-adgm-registered-entities/annual-filings/annual-accounts",
    "https://www.adgm.com/operating-in-adgm/post-registration-services/letters-and-permits"
]

settings = Settings()

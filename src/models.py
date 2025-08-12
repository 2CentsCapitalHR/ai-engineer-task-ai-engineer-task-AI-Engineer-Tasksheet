"""Data models for ADGM Corporate Agent."""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class DocumentType(str, Enum):
    """Supported document types."""
    ARTICLES_OF_ASSOCIATION = "Articles of Association"
    MEMORANDUM_OF_ASSOCIATION = "Memorandum of Association"
    INCORPORATION_APPLICATION = "Incorporation Application Form"
    UBO_DECLARATION = "UBO Declaration Form"
    BOARD_RESOLUTION = "Board Resolution Templates"
    REGISTER_MEMBERS_DIRECTORS = "Register of Members and Directors"
    SHAREHOLDER_RESOLUTION = "Shareholder Resolution Templates"
    CHANGE_ADDRESS_NOTICE = "Change of Registered Address Notice"
    EMPLOYMENT_CONTRACT = "Employment Contract"
    COMMERCIAL_AGREEMENT = "Commercial Agreement"
    COMPLIANCE_POLICY = "Compliance Policy"
    OTHER = "Other"


class ProcessType(str, Enum):
    """ADGM legal processes."""
    COMPANY_INCORPORATION = "Company Incorporation"
    LICENSE_APPLICATION = "License Application"
    EMPLOYMENT_SETUP = "Employment Setup"
    COMMERCIAL_AGREEMENT = "Commercial Agreement"
    COMPLIANCE_FILING = "Compliance Filing"
    OTHER = "Other"


class SeverityLevel(str, Enum):
    """Issue severity levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class DocumentIssue(BaseModel):
    """Represents an issue found in a document."""
    document: str = Field(description="Name of the document")
    section: Optional[str] = Field(default=None, description="Specific section or clause")
    issue: str = Field(description="Description of the issue")
    severity: SeverityLevel = Field(description="Severity level of the issue")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix or improvement")
    adgm_reference: Optional[str] = Field(default=None, description="Relevant ADGM law or regulation")
    line_number: Optional[int] = Field(default=None, description="Line number where issue was found")


class DocumentAnalysis(BaseModel):
    """Analysis result for a single document."""
    filename: str = Field(description="Original filename")
    document_type: DocumentType = Field(description="Identified document type")
    confidence: float = Field(description="Confidence in document type identification")
    issues: List[DocumentIssue] = Field(default=[], description="Issues found in the document")
    compliance_score: float = Field(description="Overall compliance score (0-100)")
    word_count: int = Field(description="Total word count")
    processed_at: datetime = Field(default_factory=datetime.now)


class ProcessAnalysis(BaseModel):
    """Analysis result for the entire process."""
    process_type: ProcessType = Field(description="Identified legal process")
    documents_uploaded: int = Field(description="Number of documents uploaded")
    required_documents: int = Field(description="Number of required documents")
    missing_documents: List[str] = Field(default=[], description="List of missing required documents")
    document_analyses: List[DocumentAnalysis] = Field(description="Individual document analyses")
    overall_compliance_score: float = Field(description="Overall process compliance score")
    recommendations: List[str] = Field(default=[], description="General recommendations")
    processed_at: datetime = Field(default_factory=datetime.now)


class ADGMRule(BaseModel):
    """Represents an ADGM rule or regulation."""
    rule_id: str = Field(description="Unique identifier for the rule")
    title: str = Field(description="Title of the rule")
    content: str = Field(description="Content of the rule")
    category: str = Field(description="Category of the rule")
    source_url: Optional[str] = Field(description="Source URL")
    last_updated: Optional[datetime] = Field(description="Last update date")


class CommentInsertion(BaseModel):
    """Represents a comment to be inserted in a document."""
    paragraph_index: int = Field(description="Index of paragraph to comment on")
    comment_text: str = Field(description="Text of the comment")
    highlight_text: Optional[str] = Field(description="Text to highlight")
    comment_type: str = Field(description="Type of comment (issue, suggestion, etc.)")


class ProcessingResult(BaseModel):
    """Final processing result."""
    success: bool = Field(description="Whether processing was successful")
    analysis: Optional[ProcessAnalysis] = Field(description="Analysis results")
    output_file_path: Optional[str] = Field(description="Path to the marked-up output file")
    error_message: Optional[str] = Field(description="Error message if processing failed")
    processing_time: float = Field(description="Processing time in seconds")

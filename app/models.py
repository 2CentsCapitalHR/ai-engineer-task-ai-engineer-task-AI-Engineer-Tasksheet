"""
Pydantic models for ADGM Corporate Agent
"""
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    """Document types supported by the system"""
    MEMORANDUM = "memorandum"
    ARTICLES = "articles"
    APPLICATION = "application"
    BOARD_RESOLUTION = "board_resolution"
    UNKNOWN = "unknown"

class ProcessingStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class FlagSeverity(str, Enum):
    """Severity levels for document flags"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class DocumentFlag(BaseModel):
    """Issues or flags identified in document"""
    severity: FlagSeverity
    title: str
    description: str
    location: Optional[str] = None
    suggested_fix: Optional[str] = None
    section: Optional[str] = None
    line_number: Optional[int] = None

class ComplianceCheck(BaseModel):
    """Individual compliance check result"""
    section: str
    status: bool
    description: str
    requirement: str
    importance: str = "mandatory"
    details: Optional[Dict] = None
    suggestions: Optional[List[str]] = None

class DocumentAnalysis(BaseModel):
    """Complete document analysis results"""
    document_id: str
    file_path: str
    document_type: DocumentType
    status: ProcessingStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    compliance_score: float = 0.0
    completeness_score: float = 0.0
    flags: List[DocumentFlag] = Field(default_factory=list)
    compliance_checks: List[ComplianceCheck] = Field(default_factory=list)
    missing_sections: List[str] = Field(default_factory=list)
    analysis_summary: Optional[str] = None
    contextual_recommendations: Optional[List[str]] = None
    structure_analysis: Optional[Dict] = None

class AnalysisReport(BaseModel):
    """Detailed analysis report"""
    document_id: str
    document_name: str
    document_type: DocumentType
    overall_status: str
    compliance_score: float
    completeness_score: float
    critical_issues: int
    warnings: int
    info_items: int
    flags: List[DocumentFlag]
    compliance_checks: List[ComplianceCheck]
    missing_documents: List[str]
    executive_summary: str
    recommendations: List[str]
    generated_at: datetime = Field(default_factory=datetime.now)

class ProcessingRequest(BaseModel):
    """Document processing request"""
    document_id: str
    file_path: str
    document_type: Optional[DocumentType] = None
    priority: int = 1
    callback_url: Optional[str] = None

class ADGMValidationRequest(BaseModel):
    """Direct content validation request"""
    content: str
    document_type: DocumentType
    validation_type: Optional[str] = "full"
    include_recommendations: bool = True

class APIResponse(BaseModel):
    """Standard API response format"""
    success: bool
    message: str
    data: Optional[Dict] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class KnowledgeBaseStats(BaseModel):
    """Knowledge base statistics"""
    total_documents: int
    collections: Dict[str, int]
    last_updated: datetime
    embedding_model: str
    storage_size: str

class DocumentTemplate(BaseModel):
    """Document template metadata"""
    template_id: str
    name: str
    document_type: DocumentType
    description: str
    sections: List[str]
    variables: Dict[str, str]
    created_at: datetime
    updated_at: datetime

class SearchResult(BaseModel):
    """Knowledge base search result"""
    content: str
    document_type: str
    relevance_score: float
    source: str
    metadata: Optional[Dict] = None

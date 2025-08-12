"""Main processing engine that orchestrates document analysis."""

import time
from pathlib import Path
from typing import List, Dict, Optional
import logging
from datetime import datetime

from .document_parser import DocumentParser
from .compliance_checker import ADGMComplianceChecker
from .checklist_verifier import DocumentChecklistVerifier
from .document_annotator import DocumentAnnotator
from ..rag.vector_store import ADGMVectorStore
from ..rag.rag_system import ADGMRAGSystem
from ..models import (
    ProcessingResult, ProcessAnalysis, DocumentAnalysis, 
    DocumentType, ProcessType, SeverityLevel
)

logger = logging.getLogger(__name__)


class ADGMProcessingEngine:
    """Main processing engine for ADGM document analysis."""
    
    def __init__(self, vector_store: ADGMVectorStore):
        self.document_parser = DocumentParser()
        self.compliance_checker = ADGMComplianceChecker()
        self.checklist_verifier = DocumentChecklistVerifier()
        self.document_annotator = DocumentAnnotator()
        self.rag_system = ADGMRAGSystem(vector_store)
        self.vector_store = vector_store
    
    def process_documents(self, file_paths: List[str], output_dir: str = "data/outputs") -> ProcessingResult:
        """Process multiple documents and return comprehensive analysis."""
        
        start_time = time.time()
        
        try:
            logger.info(f"Starting processing of {len(file_paths)} documents")
            
            # Step 1: Parse all documents
            parsed_documents = []
            for file_path in file_paths:
                try:
                    parsed_doc = self.document_parser.parse_document(file_path)
                    parsed_documents.append(parsed_doc)
                    logger.info(f"Parsed: {parsed_doc['filename']}")
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")
                    continue
            
            if not parsed_documents:
                return ProcessingResult(
                    success=False,
                    analysis=None,
                    output_file_path=None,
                    error_message="No documents could be parsed",
                    processing_time=time.time() - start_time
                )
            
            # Step 2: Identify process type
            process_type, process_confidence = self.checklist_verifier.identify_process_type(parsed_documents)
            logger.info(f"Identified process: {process_type.value} (confidence: {process_confidence:.2f})")
            
            # Step 3: Verify document completeness
            completeness_info = self.checklist_verifier.verify_document_completeness(
                parsed_documents, process_type
            )
            
            # Step 4: Analyze each document
            document_analyses = []
            for parsed_doc in parsed_documents:
                analysis = self._analyze_single_document(parsed_doc)
                document_analyses.append(analysis)
            
            # Step 5: Create process analysis
            process_analysis = ProcessAnalysis(
                process_type=process_type,
                documents_uploaded=len(parsed_documents),
                required_documents=completeness_info['total_required'],
                missing_documents=completeness_info['missing_documents'],
                document_analyses=document_analyses,
                overall_compliance_score=self._calculate_overall_score(document_analyses),
                recommendations=self._generate_process_recommendations(
                    completeness_info, document_analyses, process_type
                )
            )
            
            # Step 6: Generate annotated documents
            output_files = []
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            for i, (parsed_doc, analysis) in enumerate(zip(parsed_documents, document_analyses)):
                if analysis.issues:
                    try:
                        # Annotate document with comments
                        annotated_doc = self.document_annotator.annotate_document(
                            parsed_doc['docx_object'], 
                            analysis.issues,
                            parsed_doc['text_content']
                        )
                        
                        # Save annotated document
                        output_filename = f"reviewed_{parsed_doc['filename']}"
                        output_path = Path(output_dir) / output_filename
                        
                        self.document_parser.save_document_with_comments(
                            annotated_doc, str(output_path)
                        )
                        
                        output_files.append(str(output_path))
                        logger.info(f"Created annotated document: {output_filename}")
                        
                    except Exception as e:
                        logger.error(f"Failed to create annotated document for {parsed_doc['filename']}: {e}")
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                analysis=process_analysis,
                output_file_path=output_files[0] if output_files else None,
                error_message=None,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return ProcessingResult(
                success=False,
                analysis=None,
                output_file_path=None,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def _analyze_single_document(self, parsed_doc: Dict) -> DocumentAnalysis:
        """Analyze a single document for compliance issues."""
        
        try:
            document_type = parsed_doc['document_type']
            text_content = parsed_doc['text_content']
            structured_content = parsed_doc['structured_content']
            
            # Get compliance issues from rule-based checker
            compliance_issues = self.compliance_checker.check_compliance(
                text_content, document_type, structured_content
            )
            
            # Get additional issues from RAG system
            rag_issues = self.rag_system.analyze_document_compliance(
                text_content, document_type.value
            )
            
            # Get red flags from RAG system
            red_flags = self.rag_system.identify_red_flags(
                text_content, document_type.value
            )
            
            # Combine all issues
            all_issues = compliance_issues + rag_issues + red_flags
            
            # Remove duplicates
            unique_issues = self._deduplicate_issues(all_issues)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(unique_issues, len(text_content.split()))
            
            return DocumentAnalysis(
                filename=parsed_doc['filename'],
                document_type=document_type,
                confidence=parsed_doc['type_confidence'],
                issues=unique_issues,
                compliance_score=compliance_score,
                word_count=parsed_doc['word_count']
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze document {parsed_doc['filename']}: {e}")
            
            # Return basic analysis with error
            return DocumentAnalysis(
                filename=parsed_doc['filename'],
                document_type=parsed_doc.get('document_type', DocumentType.OTHER),
                confidence=0.0,
                issues=[],
                compliance_score=0.0,
                word_count=parsed_doc.get('word_count', 0)
            )
    
    def _deduplicate_issues(self, issues: List) -> List:
        """Remove duplicate issues based on content similarity."""
        
        unique_issues = []
        seen_issues = set()
        
        for issue in issues:
            # Create a signature for the issue
            signature = f"{issue.section}_{issue.issue}_{issue.severity.value}"
            
            if signature not in seen_issues:
                seen_issues.add(signature)
                unique_issues.append(issue)
        
        return unique_issues
    
    def _calculate_compliance_score(self, issues: List, word_count: int) -> float:
        """Calculate compliance score based on issues found."""
        
        if not issues:
            return 100.0
        
        # Weight issues by severity
        severity_weights = {
            SeverityLevel.LOW: 1,
            SeverityLevel.MEDIUM: 3,
            SeverityLevel.HIGH: 7,
            SeverityLevel.CRITICAL: 15
        }
        
        total_penalty = sum(severity_weights.get(issue.severity, 1) for issue in issues)
        
        # Normalize by document length (longer documents can have more issues)
        normalized_penalty = total_penalty / max(word_count / 100, 1)  # Per 100 words
        
        # Calculate score (100 - penalty, minimum 0)
        score = max(0, 100 - normalized_penalty)
        
        return round(score, 1)
    
    def _calculate_overall_score(self, document_analyses: List[DocumentAnalysis]) -> float:
        """Calculate overall compliance score for all documents."""
        
        if not document_analyses:
            return 0.0
        
        # Weight by document importance and word count
        total_weighted_score = 0
        total_weight = 0
        
        for analysis in document_analyses:
            # Weight by word count (longer documents have more weight)
            weight = max(analysis.word_count / 100, 1)
            total_weighted_score += analysis.compliance_score * weight
            total_weight += weight
        
        return round(total_weighted_score / total_weight, 1) if total_weight > 0 else 0.0
    
    def _generate_process_recommendations(self, completeness_info: Dict, 
                                        document_analyses: List[DocumentAnalysis],
                                        process_type: ProcessType) -> List[str]:
        """Generate recommendations for the entire process."""
        
        recommendations = []
        
        # Document completeness recommendations
        if not completeness_info['is_complete']:
            missing_count = len(completeness_info['missing_documents'])
            recommendations.append(
                f"⚠️ Missing {missing_count} required document(s) for {process_type.value}"
            )
            
            for missing_doc in completeness_info['missing_documents'][:3]:  # Show top 3
                recommendations.append(f"📄 Upload required document: {missing_doc}")
        
        # Compliance recommendations
        critical_issues = []
        high_issues = []
        
        for analysis in document_analyses:
            for issue in analysis.issues:
                if issue.severity == SeverityLevel.CRITICAL:
                    critical_issues.append(issue)
                elif issue.severity == SeverityLevel.HIGH:
                    high_issues.append(issue)
        
        if critical_issues:
            recommendations.append(f"🚨 Address {len(critical_issues)} critical compliance issue(s)")
        
        if high_issues:
            recommendations.append(f"🔴 Review {len(high_issues)} high-priority issue(s)")
        
        # Overall score recommendations
        overall_score = self._calculate_overall_score(document_analyses)
        
        if overall_score < 60:
            recommendations.append("📈 Overall compliance score is below 60% - significant improvements needed")
        elif overall_score < 80:
            recommendations.append("📊 Overall compliance score could be improved - review flagged issues")
        else:
            recommendations.append("✅ Good overall compliance score - minor improvements recommended")
        
        # Process-specific recommendations
        if process_type == ProcessType.COMPANY_INCORPORATION:
            recommendations.extend([
                "🏛️ Ensure all incorporation documents are properly executed",
                "📝 Verify company name availability with ADGM Registration Authority",
                "🏢 Confirm registered office address is within ADGM jurisdiction"
            ])
        
        return recommendations[:10]  # Limit to top 10 recommendations

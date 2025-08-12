"""Document checklist verification system for ADGM processes."""

from typing import List, Dict, Optional, Tuple
import logging
from ..models import DocumentType, ProcessType
from ..config import ADGM_PROCESS_REQUIREMENTS, ADGM_DOCUMENT_TYPES

logger = logging.getLogger(__name__)


class DocumentChecklistVerifier:
    """Verifies document completeness against ADGM process requirements."""
    
    def __init__(self):
        self.process_requirements = self._load_process_requirements()
        self.document_type_indicators = self._create_document_indicators()
    
    def identify_process_type(self, uploaded_documents: List[Dict]) -> Tuple[ProcessType, float]:
        """Identify the legal process based on uploaded documents."""
        
        # Extract document types from uploaded documents
        doc_types = [doc.get('document_type', DocumentType.OTHER) for doc in uploaded_documents]
        doc_type_names = [doc_type.value if hasattr(doc_type, 'value') else str(doc_type) 
                         for doc_type in doc_types]
        
        # Score each process type based on document matches
        process_scores = {}
        
        for process_type, required_docs in self.process_requirements.items():
            score = 0
            total_required = len(required_docs)
            
            for required_doc in required_docs:
                # Check if this required document type is present
                if any(self._documents_match(required_doc, doc_name) 
                      for doc_name in doc_type_names):
                    score += 1
            
            # Calculate confidence as percentage of required documents present
            confidence = (score / total_required) if total_required > 0 else 0
            process_scores[process_type] = confidence
        
        # Find the best match
        if process_scores:
            best_process = max(process_scores, key=process_scores.get)
            best_confidence = process_scores[best_process]
            
            # Only return if confidence is above threshold
            if best_confidence >= 0.4:  # At least 40% of required documents present
                return ProcessType(best_process), best_confidence
        
        return ProcessType.OTHER, 0.0
    
    def verify_document_completeness(self, uploaded_documents: List[Dict], 
                                   process_type: ProcessType) -> Dict:
        """Verify if all required documents are present for the process."""
        
        required_docs = self.process_requirements.get(process_type.value, [])
        uploaded_doc_types = [doc.get('document_type', DocumentType.OTHER) 
                             for doc in uploaded_documents]
        uploaded_doc_names = [doc_type.value if hasattr(doc_type, 'value') else str(doc_type) 
                             for doc_type in uploaded_doc_types]
        
        # Find missing documents
        missing_documents = []
        present_documents = []
        
        for required_doc in required_docs:
            is_present = any(self._documents_match(required_doc, doc_name) 
                           for doc_name in uploaded_doc_names)
            
            if is_present:
                present_documents.append(required_doc)
            else:
                missing_documents.append(required_doc)
        
        # Calculate completeness percentage
        total_required = len(required_docs)
        total_present = len(present_documents)
        completeness_percentage = (total_present / total_required * 100) if total_required > 0 else 100
        
        return {
            'process_type': process_type.value,
            'total_required': total_required,
            'total_uploaded': len(uploaded_documents),
            'total_present': total_present,
            'completeness_percentage': completeness_percentage,
            'missing_documents': missing_documents,
            'present_documents': present_documents,
            'is_complete': len(missing_documents) == 0
        }
    
    def get_process_guidance(self, process_type: ProcessType) -> Dict:
        """Get guidance information for a specific process."""
        
        guidance = {
            ProcessType.COMPANY_INCORPORATION: {
                'description': 'Company incorporation in ADGM requires specific documents to establish a legal entity.',
                'typical_timeline': '2-4 weeks',
                'key_requirements': [
                    'All documents must be properly executed',
                    'UBO declaration must be complete and accurate',
                    'Registered office address must be in ADGM',
                    'Company name must be approved by ADGM RA'
                ],
                'next_steps': [
                    'Submit complete application to ADGM Registration Authority',
                    'Pay required fees',
                    'Await approval and certificate of incorporation'
                ]
            },
            ProcessType.LICENSE_APPLICATION: {
                'description': 'License application for conducting business activities in ADGM.',
                'typical_timeline': '4-8 weeks',
                'key_requirements': [
                    'Business plan must align with ADGM regulations',
                    'Financial projections must be realistic',
                    'Compliance manual must address all relevant regulations'
                ],
                'next_steps': [
                    'Submit application to relevant ADGM authority',
                    'Undergo regulatory review',
                    'Address any queries or requirements'
                ]
            },
            ProcessType.EMPLOYMENT_SETUP: {
                'description': 'Setting up employment arrangements in ADGM.',
                'typical_timeline': '1-2 weeks',
                'key_requirements': [
                    'Employment contracts must comply with ADGM Employment Regulations',
                    'HR policies must be documented',
                    'Visa and work permit requirements must be addressed'
                ],
                'next_steps': [
                    'Finalize employment documentation',
                    'Apply for work permits if required',
                    'Register with ADGM authorities'
                ]
            }
        }
        
        return guidance.get(process_type, {
            'description': 'General ADGM process',
            'typical_timeline': 'Varies',
            'key_requirements': ['Ensure all documents comply with ADGM regulations'],
            'next_steps': ['Consult with ADGM authorities for specific requirements']
        })
    
    def generate_checklist_report(self, uploaded_documents: List[Dict]) -> Dict:
        """Generate a comprehensive checklist report."""
        
        # Identify the process
        process_type, confidence = self.identify_process_type(uploaded_documents)
        
        # Verify completeness
        completeness_info = self.verify_document_completeness(uploaded_documents, process_type)
        
        # Get process guidance
        guidance = self.get_process_guidance(process_type)
        
        # Create detailed report
        report = {
            'process_identification': {
                'identified_process': process_type.value,
                'confidence': confidence,
                'identification_method': 'Document type analysis'
            },
            'document_completeness': completeness_info,
            'process_guidance': guidance,
            'recommendations': self._generate_recommendations(completeness_info, process_type),
            'uploaded_documents_analysis': self._analyze_uploaded_documents(uploaded_documents)
        }
        
        return report
    
    def _documents_match(self, required_doc: str, uploaded_doc: str) -> bool:
        """Check if an uploaded document matches a required document type."""
        
        # Normalize strings for comparison
        required_lower = required_doc.lower().strip()
        uploaded_lower = uploaded_doc.lower().strip()
        
        # Direct match
        if required_lower == uploaded_lower:
            return True
        
        # Partial matches for common variations
        match_patterns = {
            'articles of association': ['articles', 'aoa', 'articles of association'],
            'memorandum of association': ['memorandum', 'moa', 'memorandum of association'],
            'ubo declaration': ['ubo', 'beneficial owner', 'ultimate beneficial owner'],
            'board resolution': ['board resolution', 'directors resolution', 'resolution'],
            'register of members and directors': ['register', 'members register', 'directors register'],
            'shareholder resolution': ['shareholder resolution', 'shareholders resolution'],
            'employment contract': ['employment', 'contract', 'employment agreement'],
            'incorporation application': ['incorporation', 'application', 'registration application']
        }
        
        # Check if required document has specific patterns
        for pattern_key, patterns in match_patterns.items():
            if pattern_key in required_lower:
                return any(pattern in uploaded_lower for pattern in patterns)
        
        # Check if uploaded document matches any pattern for required document
        for pattern in match_patterns.get(required_lower, []):
            if pattern in uploaded_lower:
                return True
        
        return False
    
    def _generate_recommendations(self, completeness_info: Dict, process_type: ProcessType) -> List[str]:
        """Generate recommendations based on completeness analysis."""
        
        recommendations = []
        
        if not completeness_info['is_complete']:
            missing_count = len(completeness_info['missing_documents'])
            recommendations.append(
                f"You are missing {missing_count} required document(s) for {process_type.value}."
            )
            
            for missing_doc in completeness_info['missing_documents']:
                recommendations.append(f"Please upload: {missing_doc}")
        
        if completeness_info['completeness_percentage'] < 100:
            recommendations.append(
                f"Your submission is {completeness_info['completeness_percentage']:.1f}% complete."
            )
        
        # Process-specific recommendations
        if process_type == ProcessType.COMPANY_INCORPORATION:
            recommendations.extend([
                "Ensure all documents are properly executed with signatures and dates",
                "Verify that the company name is available and complies with ADGM naming rules",
                "Confirm that the registered office address is within ADGM jurisdiction"
            ])
        
        elif process_type == ProcessType.LICENSE_APPLICATION:
            recommendations.extend([
                "Review business plan to ensure it aligns with ADGM regulations",
                "Verify that all proposed activities are permitted under ADGM rules",
                "Ensure compliance manual addresses all relevant regulatory requirements"
            ])
        
        return recommendations
    
    def _analyze_uploaded_documents(self, uploaded_documents: List[Dict]) -> List[Dict]:
        """Analyze each uploaded document."""
        
        analysis = []
        
        for doc in uploaded_documents:
            doc_analysis = {
                'filename': doc.get('filename', 'Unknown'),
                'identified_type': doc.get('document_type', DocumentType.OTHER).value,
                'type_confidence': doc.get('type_confidence', 0.0),
                'word_count': doc.get('word_count', 0),
                'status': 'Recognized' if doc.get('type_confidence', 0) > 0.5 else 'Needs Review'
            }
            analysis.append(doc_analysis)
        
        return analysis
    
    def _load_process_requirements(self) -> Dict:
        """Load process requirements from configuration."""
        return ADGM_PROCESS_REQUIREMENTS
    
    def _create_document_indicators(self) -> Dict:
        """Create indicators for document type identification."""
        return ADGM_DOCUMENT_TYPES

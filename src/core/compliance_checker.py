"""ADGM compliance checking and red flag detection system."""

import re
from typing import List, Dict, Optional, Tuple
import logging
from ..models import DocumentIssue, SeverityLevel, DocumentType
from ..config import RED_FLAG_PATTERNS

logger = logging.getLogger(__name__)


class ADGMComplianceChecker:
    """Core compliance checking engine for ADGM documents."""
    
    def __init__(self):
        self.jurisdiction_patterns = self._create_jurisdiction_patterns()
        self.required_clauses = self._create_required_clauses()
        self.red_flag_patterns = self._create_red_flag_patterns()
        self.formatting_rules = self._create_formatting_rules()
    
    def check_compliance(self, document_text: str, document_type: DocumentType, 
                        structured_content: Dict) -> List[DocumentIssue]:
        """Perform comprehensive compliance check on a document."""
        issues = []
        
        # Check jurisdiction compliance
        issues.extend(self._check_jurisdiction(document_text, document_type))
        
        # Check required clauses
        issues.extend(self._check_required_clauses(document_text, document_type))
        
        # Check formatting compliance
        issues.extend(self._check_formatting(document_text, structured_content, document_type))
        
        # Check for red flags
        issues.extend(self._detect_red_flags(document_text, document_type))
        
        # Check ADGM-specific requirements
        issues.extend(self._check_adgm_specific_requirements(document_text, document_type))
        
        return issues
    
    def _check_jurisdiction(self, text: str, doc_type: DocumentType) -> List[DocumentIssue]:
        """Check jurisdiction clauses for ADGM compliance."""
        issues = []
        text_lower = text.lower()
        
        # Check for incorrect jurisdiction references
        incorrect_jurisdictions = [
            r'uae\s+federal\s+courts?',
            r'dubai\s+courts?',
            r'abu\s+dhabi\s+courts?(?!\s+global\s+market)',
            r'emirates\s+courts?',
            r'federal\s+courts?\s+of\s+uae'
        ]
        
        for pattern in incorrect_jurisdictions:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                issues.append(DocumentIssue(
                    document=doc_type.value,
                    section="Jurisdiction Clause",
                    issue=f"Incorrect jurisdiction reference: '{match.group()}'",
                    severity=SeverityLevel.HIGH,
                    suggestion="Update jurisdiction to reference ADGM Courts",
                    adgm_reference="ADGM Companies Regulations 2020, Article 6"
                ))
        
        # Check for missing ADGM jurisdiction clause
        adgm_patterns = [
            r'adgm\s+courts?',
            r'abu\s+dhabi\s+global\s+market\s+courts?',
            r'courts?\s+of\s+adgm'
        ]
        
        has_adgm_jurisdiction = any(re.search(pattern, text_lower) for pattern in adgm_patterns)
        
        if not has_adgm_jurisdiction and doc_type in [
            DocumentType.ARTICLES_OF_ASSOCIATION,
            DocumentType.MEMORANDUM_OF_ASSOCIATION,
            DocumentType.COMMERCIAL_AGREEMENT
        ]:
            issues.append(DocumentIssue(
                document=doc_type.value,
                section="Jurisdiction Clause",
                issue="Missing ADGM jurisdiction clause",
                severity=SeverityLevel.HIGH,
                suggestion="Add clause specifying ADGM Courts jurisdiction",
                adgm_reference="ADGM Companies Regulations 2020"
            ))
        
        return issues
    
    def _check_required_clauses(self, text: str, doc_type: DocumentType) -> List[DocumentIssue]:
        """Check for required clauses based on document type."""
        issues = []
        text_lower = text.lower()
        
        required_clauses = self.required_clauses.get(doc_type, [])
        
        for clause_info in required_clauses:
            clause_name = clause_info['name']
            patterns = clause_info['patterns']
            severity = clause_info.get('severity', SeverityLevel.MEDIUM)
            
            # Check if any pattern matches
            found = any(re.search(pattern, text_lower) for pattern in patterns)
            
            if not found:
                issues.append(DocumentIssue(
                    document=doc_type.value,
                    section=clause_name,
                    issue=f"Missing required clause: {clause_name}",
                    severity=severity,
                    suggestion=clause_info.get('suggestion', f"Add {clause_name} clause"),
                    adgm_reference=clause_info.get('reference', "ADGM Regulations")
                ))
        
        return issues
    
    def _check_formatting(self, text: str, structured_content: Dict, 
                         doc_type: DocumentType) -> List[DocumentIssue]:
        """Check document formatting compliance."""
        issues = []
        
        # Check for signature sections
        if doc_type in [DocumentType.ARTICLES_OF_ASSOCIATION, DocumentType.BOARD_RESOLUTION]:
            if not structured_content.get('signatures'):
                issues.append(DocumentIssue(
                    document=doc_type.value,
                    section="Signature Section",
                    issue="Missing signature section",
                    severity=SeverityLevel.MEDIUM,
                    suggestion="Add proper signature section with date and witness fields",
                    adgm_reference="ADGM Document Standards"
                ))
        
        # Check for proper numbering
        sections = structured_content.get('sections', [])
        if len(sections) > 0:
            # Check if sections are properly numbered
            numbered_sections = [s for s in sections if re.match(r'^\d+\.', s['text'])]
            if len(numbered_sections) < len(sections) * 0.5:  # Less than 50% numbered
                issues.append(DocumentIssue(
                    document=doc_type.value,
                    section="Document Structure",
                    issue="Inconsistent section numbering",
                    severity=SeverityLevel.LOW,
                    suggestion="Use consistent numbering for all sections",
                    adgm_reference="ADGM Document Formatting Guidelines"
                ))
        
        # Check for tables in documents that should have them
        if doc_type == DocumentType.REGISTER_MEMBERS_DIRECTORS:
            if not structured_content.get('tables'):
                issues.append(DocumentIssue(
                    document=doc_type.value,
                    section="Data Structure",
                    issue="Missing tabular format for member/director information",
                    severity=SeverityLevel.MEDIUM,
                    suggestion="Use table format for member and director details",
                    adgm_reference="ADGM Register Requirements"
                ))
        
        return issues
    
    def _detect_red_flags(self, text: str, doc_type: DocumentType) -> List[DocumentIssue]:
        """Detect red flags in the document."""
        issues = []
        text_lower = text.lower()
        
        # Ambiguous language red flags
        ambiguous_patterns = [
            r'\bmay\s+(?:be|have|do)',
            r'\bshould\s+(?:be|have|do)',
            r'\bmight\s+(?:be|have|do)',
            r'\bpossibly',
            r'\bperhaps',
            r'\bif\s+possible'
        ]
        
        for pattern in ambiguous_patterns:
            matches = list(re.finditer(pattern, text_lower))
            if len(matches) > 3:  # Too many ambiguous terms
                issues.append(DocumentIssue(
                    document=doc_type.value,
                    section="Language Clarity",
                    issue="Excessive use of ambiguous language",
                    severity=SeverityLevel.MEDIUM,
                    suggestion="Use definitive language (shall, will, must) instead of ambiguous terms",
                    adgm_reference="ADGM Drafting Standards"
                ))
                break
        
        # Missing essential information
        if doc_type == DocumentType.ARTICLES_OF_ASSOCIATION:
            essential_info = [
                (r'share\s+capital', "Share capital information"),
                (r'registered\s+office', "Registered office address"),
                (r'objects?\s+of\s+the\s+company', "Company objects")
            ]
            
            for pattern, info_name in essential_info:
                if not re.search(pattern, text_lower):
                    issues.append(DocumentIssue(
                        document=doc_type.value,
                        section=info_name,
                        issue=f"Missing {info_name.lower()}",
                        severity=SeverityLevel.HIGH,
                        suggestion=f"Include {info_name.lower()} in the document",
                        adgm_reference="ADGM Companies Regulations"
                    ))
        
        # Date format issues
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{1,2}-\d{1,2}-\d{2,4}'   # MM-DD-YYYY or DD-MM-YYYY
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, text):
                issues.append(DocumentIssue(
                    document=doc_type.value,
                    section="Date Format",
                    issue="Inconsistent date format detected",
                    severity=SeverityLevel.LOW,
                    suggestion="Use consistent date format (DD Month YYYY)",
                    adgm_reference="ADGM Document Standards"
                ))
                break
        
        return issues
    
    def _check_adgm_specific_requirements(self, text: str, doc_type: DocumentType) -> List[DocumentIssue]:
        """Check ADGM-specific requirements."""
        issues = []
        text_lower = text.lower()
        
        # Check for ADGM registration number format
        if doc_type in [DocumentType.ARTICLES_OF_ASSOCIATION, DocumentType.MEMORANDUM_OF_ASSOCIATION]:
            adgm_reg_pattern = r'adgm\s*-?\s*\d+'
            if not re.search(adgm_reg_pattern, text_lower):
                issues.append(DocumentIssue(
                    document=doc_type.value,
                    section="Registration Details",
                    issue="Missing or incorrect ADGM registration number format",
                    severity=SeverityLevel.MEDIUM,
                    suggestion="Include proper ADGM registration number (ADGM-XXXXXX)",
                    adgm_reference="ADGM Registration Requirements"
                ))
        
        # Check for proper ADGM address format
        if 'abu dhabi global market' not in text_lower and 'adgm' in text_lower:
            # Check if ADGM is mentioned but full name is not used
            issues.append(DocumentIssue(
                document=doc_type.value,
                section="ADGM Reference",
                issue="ADGM abbreviation used without full name",
                severity=SeverityLevel.LOW,
                suggestion="Use full name 'Abu Dhabi Global Market (ADGM)' on first reference",
                adgm_reference="ADGM Style Guide"
            ))
        
        return issues
    
    def _create_jurisdiction_patterns(self) -> Dict:
        """Create patterns for jurisdiction checking."""
        return {
            'correct': [
                r'adgm\s+courts?',
                r'abu\s+dhabi\s+global\s+market\s+courts?',
                r'courts?\s+of\s+adgm'
            ],
            'incorrect': [
                r'uae\s+federal\s+courts?',
                r'dubai\s+courts?',
                r'abu\s+dhabi\s+courts?(?!\s+global\s+market)'
            ]
        }
    
    def _create_required_clauses(self) -> Dict[DocumentType, List[Dict]]:
        """Create required clauses for each document type."""
        return {
            DocumentType.ARTICLES_OF_ASSOCIATION: [
                {
                    'name': 'Company Name',
                    'patterns': [r'company\s+name', r'name\s+of\s+the\s+company'],
                    'severity': SeverityLevel.HIGH,
                    'reference': 'ADGM Companies Regulations 2020, Art. 15'
                },
                {
                    'name': 'Share Capital',
                    'patterns': [r'share\s+capital', r'authorized\s+capital'],
                    'severity': SeverityLevel.HIGH,
                    'reference': 'ADGM Companies Regulations 2020, Art. 25'
                },
                {
                    'name': 'Directors Powers',
                    'patterns': [r'directors?\s+powers?', r'board\s+powers?'],
                    'severity': SeverityLevel.MEDIUM,
                    'reference': 'ADGM Companies Regulations 2020, Art. 45'
                }
            ],
            DocumentType.MEMORANDUM_OF_ASSOCIATION: [
                {
                    'name': 'Company Objects',
                    'patterns': [r'objects?\s+of\s+the\s+company', r'business\s+objects?'],
                    'severity': SeverityLevel.HIGH,
                    'reference': 'ADGM Companies Regulations 2020, Art. 12'
                },
                {
                    'name': 'Liability Clause',
                    'patterns': [r'liability\s+of\s+members', r'limited\s+liability'],
                    'severity': SeverityLevel.HIGH,
                    'reference': 'ADGM Companies Regulations 2020, Art. 18'
                }
            ]
        }
    
    def _create_red_flag_patterns(self) -> Dict:
        """Create red flag detection patterns."""
        return RED_FLAG_PATTERNS
    
    def _create_formatting_rules(self) -> Dict:
        """Create formatting rules for different document types."""
        return {
            'general': {
                'requires_signatures': True,
                'requires_dates': True,
                'requires_numbering': True
            },
            'legal_documents': {
                'requires_jurisdiction': True,
                'requires_governing_law': True,
                'requires_proper_citations': True
            }
        }

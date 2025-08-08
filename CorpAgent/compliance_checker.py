import re
from typing import List, Dict, Any
from rag_system import RAGSystem
from adgm_data import ADGM_DOCUMENT_CHECKLISTS, ADGM_COMPLIANCE_RULES

class ComplianceChecker:
    """Handles ADGM compliance checking and document validation."""
    
    def __init__(self, rag_system: RAGSystem):
        self.rag_system = rag_system
        self.compliance_rules = ADGM_COMPLIANCE_RULES
        self.document_checklists = ADGM_DOCUMENT_CHECKLISTS
    
    def analyze_document(self, content: Dict, document_type: str) -> Dict[str, Any]:
        """Analyze a single document for compliance issues."""
        
        # Combine all text for analysis
        full_text = self._extract_full_text(content)
        
        # Use RAG for intelligent analysis
        rag_analysis = self.rag_system.analyze_with_rag(full_text, document_type)
        
        # Apply rule-based checks
        rule_based_issues = self._apply_rule_based_checks(full_text, document_type)
        
        # Combine results
        all_issues = rag_analysis.get('issues', []) + rule_based_issues
        
        # Remove duplicates and sort by severity
        unique_issues = self._deduplicate_issues(all_issues)
        sorted_issues = sorted(unique_issues, key=lambda x: self._severity_score(x['severity']), reverse=True)
        
        return {
            'document_type': document_type,
            'compliance_score': rag_analysis.get('compliance_score', 0),
            'issues': sorted_issues,
            'missing_clauses': rag_analysis.get('missing_clauses', []),
            'recommendations': rag_analysis.get('recommendations', [])
        }
    
    def check_process_compliance(self, analyzed_documents: List[Dict], process_type: str) -> Dict[str, Any]:
        """Check if all required documents are present for a specific process."""
        
        if process_type == "Auto-detect from documents":
            process_type = self._detect_process_type(analyzed_documents)
        
        # Get required documents for this process
        required_docs = self.document_checklists.get(process_type, [])
        
        # Get uploaded document types
        uploaded_types = [doc['document_type'] for doc in analyzed_documents]
        
        # Find missing documents
        missing_docs = []
        for required_doc in required_docs:
            if not any(self._doc_type_matches(uploaded_type, required_doc) for uploaded_type in uploaded_types):
                missing_docs.append(required_doc)
        
        # Calculate completion percentage
        completion_percentage = ((len(required_docs) - len(missing_docs)) / len(required_docs) * 100) if required_docs else 100
        
        return {
            'process_type': process_type,
            'required_documents': required_docs,
            'uploaded_documents': len(analyzed_documents),
            'missing_documents': missing_docs,
            'completion_percentage': completion_percentage,
            'compliance_status': 'Complete' if not missing_docs else 'Incomplete'
        }
    
    def _extract_full_text(self, content: Dict) -> str:
        """Extract all text from document content."""
        full_text = ""
        
        # Add paragraphs
        for para in content.get('paragraphs', []):
            full_text += para['text'] + "\n"
        
        # Add table content
        for table in content.get('tables', []):
            for row in table:
                full_text += " ".join(row) + "\n"
        
        # Add headers and footers
        for header in content.get('headers', []):
            full_text += header + "\n"
        for footer in content.get('footers', []):
            full_text += footer + "\n"
        
        return full_text
    
    def _apply_rule_based_checks(self, text: str, document_type: str) -> List[Dict]:
        """Apply rule-based compliance checks."""
        issues = []
        
        # Get rules for this document type
        rules = self.compliance_rules.get(document_type, {})
        
        for rule_name, rule_config in rules.items():
            if self._check_rule(text, rule_config):
                issues.append({
                    'section': rule_config.get('section', 'General'),
                    'issue': rule_config['issue'],
                    'severity': rule_config['severity'],
                    'suggestion': rule_config.get('suggestion', ''),
                    'adgm_reference': rule_config.get('adgm_reference', '')
                })
        
        return issues
    
    def _check_rule(self, text: str, rule_config: Dict) -> bool:
        """Check if a specific rule violation exists."""
        check_type = rule_config.get('check_type', 'missing_pattern')
        pattern = rule_config.get('pattern', '')
        
        if check_type == 'missing_pattern':
            # Check if required pattern is missing
            return not re.search(pattern, text, re.IGNORECASE)
        elif check_type == 'forbidden_pattern':
            # Check if forbidden pattern exists
            return bool(re.search(pattern, text, re.IGNORECASE))
        elif check_type == 'custom':
            # Custom validation logic
            return rule_config.get('validator', lambda x: False)(text)
        
        return False
    
    def _detect_process_type(self, analyzed_documents: List[Dict]) -> str:
        """Detect the legal process based on uploaded documents."""
        doc_types = [doc['document_type'] for doc in analyzed_documents]
        
        # Check for company formation documents
        formation_docs = [
            'Articles of Association',
            'Memorandum of Association', 
            'Incorporation Application',
            'UBO Declaration'
        ]
        
        if any(doc_type in formation_docs for doc_type in doc_types):
            return 'Company Incorporation'
        
        # Check for licensing documents
        if any('License' in doc_type for doc_type in doc_types):
            return 'Licensing Application'
        
        # Check for employment documents
        if any('Employment' in doc_type for doc_type in doc_types):
            return 'Employment Contracts'
        
        # Default to general compliance
        return 'Compliance Review'
    
    def _doc_type_matches(self, uploaded_type: str, required_type: str) -> bool:
        """Check if uploaded document type matches required type."""
        # Normalize strings for comparison
        uploaded_norm = uploaded_type.lower().replace(' ', '').replace('_', '')
        required_norm = required_type.lower().replace(' ', '').replace('_', '')
        
        # Check for exact match or partial match
        return uploaded_norm in required_norm or required_norm in uploaded_norm
    
    def _deduplicate_issues(self, issues: List[Dict]) -> List[Dict]:
        """Remove duplicate issues based on section and issue text."""
        seen = set()
        unique_issues = []
        
        for issue in issues:
            key = (issue.get('section', ''), issue.get('issue', ''))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues
    
    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting."""
        scores = {'High': 3, 'Medium': 2, 'Low': 1}
        return scores.get(severity, 0)

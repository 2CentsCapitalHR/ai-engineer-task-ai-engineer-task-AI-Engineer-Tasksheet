import json
from typing import List, Dict, Any
from pathlib import Path

class ComplianceChecker:
    """Custom compliance checker for ADGM corporate documents."""
    
    def __init__(self):
        self.checklist = None
    
    def load_checklist(self, checklist_path: str):
        """Load the compliance checklist."""
        with open(checklist_path, 'r') as f:
            self.checklist = json.load(f)
    
    def generate_report(self, documents: List[Dict[str, Any]], process_type: str, checklist: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a compliance report for uploaded documents."""
        
        uploaded_doc_types = [doc.get('type', 'unknown') for doc in documents]
        required_docs = checklist.get('required_documents', [])
        
        # Find missing documents
        missing_documents = [doc for doc in required_docs if doc not in uploaded_doc_types]
        
        # Generate issues based on document analysis
        issues = []
        
        for doc in documents:
            # Check for required sections
            content = doc.get('content', '').lower()
            required_sections = checklist.get('required_sections', {})
            
            for section, requirements in required_sections.items():
                if section.lower() not in content:
                    issues.append({
                        'document': doc.get('filename', 'Unknown'),
                        'section': section,
                        'description': f'Missing required section: {section}',
                        'severity': 'high',
                        'suggestion': f'Add the {section} section as per ADGM requirements',
                        'reference': requirements.get('reference', 'ADGM regulations')
                    })
        
        return {
            'total_documents': len(documents),
            'required_documents': len(required_docs),
            'missing_documents': missing_documents,
            'uploaded_documents': documents,
            'issues': issues,
            'process_type': process_type,
            'compliance_score': max(0, 100 - (len(missing_documents) * 20) - (len(issues) * 10))
        }
    
    def check_document(self, document: Dict[str, Any], checklist: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check a single document against compliance requirements."""
        issues = []
        
        # Check document type
        doc_type = document.get('type', 'unknown')
        if doc_type not in checklist.get('allowed_document_types', []):
            issues.append({
                'document': document.get('filename', 'Unknown'),
                'section': 'Document Type',
                'description': f'Invalid document type: {doc_type}',
                'severity': 'high',
                'suggestion': f'Upload a valid document type: {", ".join(checklist.get("allowed_document_types", []))}',
                'reference': 'ADGM document requirements'
            })
        
        # Check content requirements
        content = document.get('content', '').lower()
        min_length = checklist.get('minimum_content_length', 100)
        if len(content) < min_length:
            issues.append({
                'document': document.get('filename', 'Unknown'),
                'section': 'Content',
                'description': f'Document content too short ({len(content)} characters)',
                'severity': 'medium',
                'suggestion': f'Ensure document has at least {min_length} characters',
                'reference': 'ADGM content requirements'
            })
        
        return issues

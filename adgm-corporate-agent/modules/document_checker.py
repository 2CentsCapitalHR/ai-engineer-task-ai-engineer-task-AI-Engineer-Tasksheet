import json
from typing import List, Dict

class DocumentChecker:
    def __init__(self):
        with open('templates/checklists.json', 'r') as f:
            self.checklists = json.load(f)
        
    def identify_process(self, documents: List[Dict]) -> str:
        """Identify which legal process user is attempting"""
        doc_types = [doc.get('document_type', 'unknown') for doc in documents]
        
        # Remove unknown types
        valid_doc_types = [dt for dt in doc_types if dt != 'unknown']
        
        if not valid_doc_types:
            return 'unknown'
        
        # Check against known processes
        best_match = 'unknown'
        highest_score = 0
        
        for process, requirements in self.checklists.items():
            required_docs = requirements.get('required_documents', [])
            optional_docs = requirements.get('optional_documents', [])
            all_docs = required_docs + optional_docs
            
            # Calculate match score
            matches = sum(1 for doc_type in valid_doc_types if doc_type in all_docs)
            score = matches / len(valid_doc_types) if valid_doc_types else 0
            
            if score > highest_score and matches > 0:
                highest_score = score
                best_match = process
        
        return best_match
    
    def check_completeness(self, documents: List[Dict], process: str) -> Dict:
        """Check if all required documents are present"""
        if process == 'unknown' or process not in self.checklists:
            return {
                'process': process,
                'documents_uploaded': len(documents),
                'required_documents': 0,
                'missing_documents': [],
                'completion_rate': 0.0
            }
        
        requirements = self.checklists[process]
        uploaded_types = [doc.get('document_type', 'unknown') for doc in documents]
        
        # Remove unknown types for analysis
        valid_uploaded_types = [dt for dt in uploaded_types if dt != 'unknown']
        
        required_docs = requirements.get('required_documents', [])
        missing_docs = []
        
        for required_doc in required_docs:
            if required_doc not in valid_uploaded_types:
                missing_docs.append(required_doc)
        
        completion_rate = 0.0
        if required_docs:
            completed = len(required_docs) - len(missing_docs)
            completion_rate = completed / len(required_docs)
        
        return {
            'process': process,
            'documents_uploaded': len(documents),
            'required_documents': len(required_docs),
            'missing_documents': missing_docs,
            'completion_rate': completion_rate
        }
    
    def detect_red_flags(self, document: Dict) -> List[Dict]:
        """Detect legal red flags in document"""
        red_flags = []
        content = document.get('content', '').lower()
        
        if not content:
            red_flags.append({
                'type': 'empty_document',
                'severity': 'high',
                'message': 'Document appears to be empty or unreadable',
                'suggestion': 'Please check the document format and content'
            })
            return red_flags
        
        # Check jurisdiction
        has_adgm = 'adgm' in content or 'abu dhabi global market' in content
        has_other_jurisdiction = any(term in content for term in [
            'uae federal', 'dubai courts', 'dubai international financial centre',
            'difc', 'emirates', 'sharjah', 'federal law'
        ])
        
        if not has_adgm and has_other_jurisdiction:
            red_flags.append({
                'type': 'jurisdiction_error',
                'severity': 'high',
                'message': 'Document references non-ADGM jurisdiction',
                'suggestion': 'Update jurisdiction clause to specify ADGM Courts and regulations'
            })
        elif not has_adgm:
            red_flags.append({
                'type': 'missing_jurisdiction',
                'severity': 'medium',
                'message': 'No clear ADGM jurisdiction specified',
                'suggestion': 'Add explicit reference to ADGM jurisdiction and governing law'
            })
        
        # Check for signature sections
        if not any(term in content for term in ['signature', 'signed', 'executed', 'witness']):
            red_flags.append({
                'type': 'missing_signature',
                'severity': 'medium',
                'message': 'No signature section found',
                'suggestion': 'Add proper signatory section with witness requirements'
            })
        
        # Check for essential clauses based on document type
        doc_type = document.get('document_type', 'unknown')
        
        if doc_type == 'articles_of_association':
            if 'share capital' not in content and 'capital' not in content:
                red_flags.append({
                    'type': 'missing_clause',
                    'severity': 'high',
                    'message': 'Share capital clause appears to be missing',
                    'suggestion': 'Include detailed share capital structure and nominal value'
                })
                
            if 'registered office' not in content:
                red_flags.append({
                    'type': 'missing_clause',
                    'severity': 'high',
                    'message': 'Registered office clause appears to be missing',
                    'suggestion': 'Include registered office address within ADGM'
                })
        
        elif doc_type == 'board_resolution':
            if not any(term in content for term in ['resolved', 'resolution', 'decided']):
                red_flags.append({
                    'type': 'missing_clause',
                    'severity': 'medium',
                    'message': 'Resolution language appears to be missing',
                    'suggestion': 'Include proper resolution language (e.g., "IT WAS RESOLVED THAT...")'
                })
        
        # Check for dates
        if not any(term in content for term in ['date', '202', '2025', 'day of']):
            red_flags.append({
                'type': 'missing_date',
                'severity': 'low',
                'message': 'No date found in document',
                'suggestion': 'Include execution date for legal validity'
            })
        
        return red_flags

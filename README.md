import docx
from docx import Document
from docx.shared import RGBColor
from docx.oxml.shared import OxmlElement, qn
import re
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RedFlag:
    document_name: str
    section: str
    issue: str
    severity: str
    line_number: int = None
    suggestion: str = None
    adgm_reference: str = None

class ADGMRedFlagDetector:
    def __init__(self):
        self.red_flags = []
        self.setup_detection_rules()
    
    def setup_detection_rules(self):
        """Define ADGM-specific detection patterns and rules"""
        
        # Jurisdiction patterns that should be flagged
        self.incorrect_jurisdictions = [
            r'UAE Federal Court',
            r'Dubai Court',
            r'Sharjah Court',
            r'UAE Courts(?!\s+of\s+ADGM)',
            r'Federal Law',
            r'UAE Civil Code',
            r'Dubai International Financial Centre',
            r'DIFC'
        ]
        
        # Required ADGM jurisdiction patterns
        self.correct_adgm_patterns = [
            r'ADGM Court',
            r'Abu Dhabi Global Market',
            r'ADGM.*jurisdiction',
            r'ADGM.*law',
            r'ADGM.*regulation'
        ]
        
        # Weak/ambiguous language patterns
        self.weak_language_patterns = [
            r'\bmay\s+(?:be|have)',
            r'\bpossibly\b',
            r'\bperhaps\b',
            r'\bmight\s+consider',
            r'\bshould\s+try\s+to',
            r'\bwill\s+attempt',
            r'\best\s+efforts',
            r'\breasonable\s+efforts(?!\s+shall)',
            r'\bsubject\s+to\s+availability'
        ]
        
        # Missing clause indicators for different document types
        self.required_clauses = {
            'articles_of_association': [
                r'registered\s+office',
                r'share\s+capital',
                r'objects?\s+of\s+the\s+company',
                r'directors?\s+appointment',
                r'general\s+meetings?'
            ],
            'memorandum_of_association': [
                r'company\s+name',
                r'registered\s+office',
                r'objects?\s+clause',
                r'liability\s+clause',
                r'share\s+capital'
            ],
            'board_resolution': [
                r'quorum',
                r'voting',
                r'chairman',
                r'secretary',
                r'date\s+of\s+meeting'
            ]
        }
        
        # Signatory section patterns
        self.signatory_patterns = [
            r'signature',
            r'signed\s+by',
            r'witness',
            r'date\s+of\s+execution',
            r'executed\s+on'
        ]

    def analyze_document(self, file_path: str) -> Dict:
        """Main analysis function"""
        try:
            doc = Document(file_path)
            document_name = file_path.split('/')[-1] if '/' in file_path else file_path
            
            # Extract full text for analysis
            full_text = self._extract_text(doc)
            
            # Detect document type
            doc_type = self._detect_document_type(full_text)
            
            # Run all red flag checks
            self._check_jurisdiction_compliance(full_text, document_name)
            self._check_weak_language(full_text, document_name)
            self._check_missing_clauses(full_text, document_name, doc_type)
            self._check_signatory_sections(full_text, document_name)
            self._check_formatting_issues(doc, document_name)
            
            # Add comments to document
            self._add_inline_comments(doc, file_path)
            
            return self._generate_report(document_name, doc_type)
            
        except Exception as e:
            return {"error": f"Failed to analyze document: {str(e)}"}

    def _extract_text(self, doc: Document) -> str:
        """Extract all text from document"""
        text_content = []
        for paragraph in doc.paragraphs:
            text_content.append(paragraph.text)
        
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text_content.append(cell.text)
        
        return '\n'.join(text_content)

    def _detect_document_type(self, text: str) -> str:
        """Detect the type of legal document"""
        text_lower = text.lower()
        
        if re.search(r'articles?\s+of\s+association', text_lower):
            return 'articles_of_association'
        elif re.search(r'memorandum\s+of\s+association', text_lower):
            return 'memorandum_of_association'
        elif re.search(r'board\s+resolution', text_lower):
            return 'board_resolution'
        elif re.search(r'shareholder\s+resolution', text_lower):
            return 'shareholder_resolution'
        elif re.search(r'employment\s+contract', text_lower):
            return 'employment_contract'
        else:
            return 'unknown'

    def _check_jurisdiction_compliance(self, text: str, doc_name: str):
        """Check for incorrect jurisdiction references"""
        lines = text.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for incorrect jurisdictions
            for pattern in self.incorrect_jurisdictions:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    self.red_flags.append(RedFlag(
                        document_name=doc_name,
                        section=f"Line {i}",
                        issue=f"Incorrect jurisdiction reference: '{match.group()}'",
                        severity="High",
                        line_number=i,
                        suggestion="Replace with 'ADGM Courts' or 'Abu Dhabi Global Market jurisdiction'",
                        adgm_reference="Per ADGM Companies Regulations 2020, Art. 6"
                    ))
        
        # Check if ADGM jurisdiction is mentioned at all
        has_adgm_jurisdiction = any(re.search(pattern, text, re.IGNORECASE) 
                                 for pattern in self.correct_adgm_patterns)
        
        if not has_adgm_jurisdiction and len(text.strip()) > 100:  # Only for substantial documents
            self.red_flags.append(RedFlag(
                document_name=doc_name,
                section="General",
                issue="No ADGM jurisdiction clause found",
                severity="High",
                suggestion="Add clause specifying ADGM jurisdiction and applicable laws",
                adgm_reference="Per ADGM Companies Regulations 2020, Art. 6"
            ))

    def _check_weak_language(self, text: str, doc_name: str):
        """Check for ambiguous or non-binding language"""
        lines = text.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern in self.weak_language_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    self.red_flags.append(RedFlag(
                        document_name=doc_name,
                        section=f"Line {i}",
                        issue=f"Weak/ambiguous language: '{match.group()}'",
                        severity="Medium",
                        line_number=i,
                        suggestion="Use definitive language like 'shall', 'will', or 'must'",
                        adgm_reference="ADGM Contract Law - definitive obligations required"
                    ))

    def _check_missing_clauses(self, text: str, doc_name: str, doc_type: str):
        """Check for missing mandatory clauses based on document type"""
        if doc_type not in self.required_clauses:
            return
        
        text_lower = text.lower()
        missing_clauses = []
        
        for required_clause in self.required_clauses[doc_type]:
            if not re.search(required_clause, text_lower):
                missing_clauses.append(required_clause)
        
        for clause in missing_clauses:
            self.red_flags.append(RedFlag(
                document_name=doc_name,
                section="Document Structure",
                issue=f"Missing required clause: {clause}",
                severity="High",
                suggestion=f"Add {clause} clause as required by ADGM regulations",
                adgm_reference=f"Per ADGM Companies Regulations 2020 - {clause} mandatory"
            ))

    def _check_signatory_sections(self, text: str, doc_name: str):
        """Check for proper signatory sections"""
        has_signature_section = any(re.search(pattern, text, re.IGNORECASE) 
                                  for pattern in self.signatory_patterns)
        
        if not has_signature_section and len(text.strip()) > 100:
            self.red_flags.append(RedFlag(
                document_name=doc_name,
                section="Execution",
                issue="Missing signatory section or execution clause",
                severity="High",
                suggestion="Add proper signature blocks with date and witness fields",
                adgm_reference="ADGM execution requirements - proper signatory format required"
            ))

    def _check_formatting_issues(self, doc: Document, doc_name: str):
        """Check for formatting and structure issues"""
        issues = []
        
        # Check if document has any content
        if len(doc.paragraphs) == 0:
            issues.append("Document appears to be empty")
        
        # Check for extremely short paragraphs that might indicate formatting issues
        short_paragraphs = [p for p in doc.paragraphs if len(p.text.strip()) > 0 and len(p.text.strip()) < 10]
        if len(short_paragraphs) > len(doc.paragraphs) * 0.5:  # More than 50% are very short
            issues.append("Potential formatting issues - many fragmented paragraphs")
        
        for issue in issues:
            self.red_flags.append(RedFlag(
                document_name=doc_name,
                section="Formatting",
                issue=issue,
                severity="Medium",
                suggestion="Review document formatting and structure"
            ))

    def _add_inline_comments(self, doc: Document, original_file_path: str):
        """Add comments to the document at relevant locations"""
        # Group red flags by line number for insertion
        line_flags = {}
        for flag in self.red_flags:
            if flag.line_number:
                if flag.line_number not in line_flags:
                    line_flags[flag.line_number] = []
                line_flags[flag.line_number].append(flag)
        
        # Add comments to paragraphs (simplified approach)
        for i, paragraph in enumerate(doc.paragraphs):
            line_num = i + 1
            if line_num in line_flags:
                # Add comment text at the end of the paragraph
                comment_text = " | ".join([f"⚠️ {flag.issue}" for flag in line_flags[line_num]])
                if paragraph.text.strip():
                    paragraph.text += f" [COMMENT: {comment_text}]"
        
        # Save the commented document
        output_path = original_file_path.replace('.docx', '_reviewed.docx')
        doc.save(output_path)
        print(f"Reviewed document saved as: {output_path}")

    def _generate_report(self, doc_name: str, doc_type: str) -> Dict:
        """Generate structured analysis report"""
        high_severity = [f for f in self.red_flags if f.severity == "High"]
        medium_severity = [f for f in self.red_flags if f.severity == "Medium"]
        
        report = {
            "document_name": doc_name,
            "document_type": doc_type,
            "analysis_timestamp": datetime.now().isoformat(),
            "total_issues": len(self.red_flags),
            "high_severity_issues": len(high_severity),
            "medium_severity_issues": len(medium_severity),
            "compliance_score": max(0, 100 - (len(high_severity) * 20 + len(medium_severity) * 10)),
            "issues_found": [
                {
                    "section": flag.section,
                    "issue": flag.issue,
                    "severity": flag.severity,
                    "line_number": flag.line_number,
                    "suggestion": flag.suggestion,
                    "adgm_reference": flag.adgm_reference
                }
                for flag in self.red_flags
            ]
        }
        
        return report

    def analyze_multiple_documents(self, file_paths: List[str]) -> Dict:
        """Analyze multiple documents and provide consolidated report"""
        all_reports = []
        
        for file_path in file_paths:
            self.red_flags = []  # Reset for each document
            report = self.analyze_document(file_path)
            all_reports.append(report)
        
        # Generate consolidated summary
        total_issues = sum(report.get('total_issues', 0) for report in all_reports)
        avg_compliance = sum(report.get('compliance_score', 0) for report in all_reports) / len(all_reports)
        
        return {
            "summary": {
                "documents_analyzed": len(file_paths),
                "total_issues_found": total_issues,
                "average_compliance_score": round(avg_compliance, 2)
            },
            "individual_reports": all_reports
        }

# Usage Example
if __name__ == "__main__":
    detector = ADGMRedFlagDetector()
    
    # Example usage:
    # report = detector.analyze_document("sample_document.docx")
    # print(json.dumps(report, indent=2))
    
    print("ADGM Red Flag Detection System initialized!")
    print("Usage: detector.analyze_document('your_document.docx')")
    print("\nFeatures:")
    print("- Detects incorrect jurisdiction references")
    print("- Identifies weak/ambiguous language")
    print("- Checks for missing mandatory clauses")
    print("- Validates signatory sections")
    print("- Adds inline comments to documents")
    print("- Generates compliance reports with ADGM references")

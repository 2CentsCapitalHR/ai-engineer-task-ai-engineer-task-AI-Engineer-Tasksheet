import json
from datetime import datetime
from typing import List, Dict

class ReportGenerator:
    def __init__(self):
        pass
    
    def generate_json_report(self, analysis_results: Dict) -> Dict:
        """Generate structured JSON report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_summary": {
                "process": analysis_results.get('process', 'unknown'),
                "documents_uploaded": analysis_results.get('documents_uploaded', 0),
                "required_documents": analysis_results.get('required_documents', 0),
                "missing_documents": analysis_results.get('missing_documents', []),
                "completion_rate": round(analysis_results.get('completion_rate', 0) * 100, 1)
            },
            "document_details": [],
            "issues_summary": {
                "total_issues": 0,
                "high_severity": 0,
                "medium_severity": 0,
                "low_severity": 0
            },
            "recommendations": []
        }
        
        # Process each document
        for doc_analysis in analysis_results.get('document_analyses', []):
            doc_detail = {
                "filename": doc_analysis.get('filename', 'unknown'),
                "document_type": doc_analysis.get('document_type', 'unknown'),
                "word_count": doc_analysis.get('word_count', 0),
                "paragraph_count": doc_analysis.get('paragraph_count', 0),
                "issues_found": []
            }
            
            # Add red flags
            for flag in doc_analysis.get('red_flags', []):
                issue = {
                    "type": flag.get('type', 'unknown'),
                    "severity": flag.get('severity', 'medium'),
                    "message": flag.get('message', ''),
                    "suggestion": flag.get('suggestion', '')
                }
                doc_detail["issues_found"].append(issue)
                
                # Update summary counts
                report["issues_summary"]["total_issues"] += 1
                severity = flag.get('severity', 'medium').lower()
                if severity == 'high':
                    report["issues_summary"]["high_severity"] += 1
                elif severity == 'medium':
                    report["issues_summary"]["medium_severity"] += 1
                else:
                    report["issues_summary"]["low_severity"] += 1
            
            report["document_details"].append(doc_detail)
        
        # Add recommendations
        if report["issues_summary"]["high_severity"] > 0:
            report["recommendations"].append("Address high-severity issues before submission to ADGM")
        
        if analysis_results.get('missing_documents'):
            report["recommendations"].append("Upload missing required documents to complete the process")
        
        if report["analysis_summary"]["completion_rate"] < 100:
            report["recommendations"].append("Ensure all required documents are uploaded for complete submission")
        
        return report
    
    def save_report(self, report: Dict, output_path: str):
        """Save report to file"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

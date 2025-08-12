"""Report generation utilities for ADGM analysis results."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..models import ProcessAnalysis, DocumentAnalysis, DocumentIssue

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates various types of reports from analysis results."""
    
    def __init__(self, output_dir: str = "data/outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_comprehensive_report(self, analysis: ProcessAnalysis, 
                                    output_filename: Optional[str] = None) -> Dict[str, str]:
        """Generate all report types and return file paths."""
        
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"adgm_analysis_{timestamp}"
        
        reports = {}
        
        try:
            # Generate JSON report
            json_path = self._generate_json_report(analysis, f"{output_filename}.json")
            reports['json'] = json_path
            
            # Generate HTML report
            html_path = self._generate_html_report(analysis, f"{output_filename}.html")
            reports['html'] = html_path
            
            # Generate CSV summary
            csv_path = self._generate_csv_summary(analysis, f"{output_filename}_summary.csv")
            reports['csv'] = csv_path
            
            # Generate executive summary
            summary_path = self._generate_executive_summary(analysis, f"{output_filename}_executive_summary.txt")
            reports['summary'] = summary_path
            
            logger.info(f"Generated {len(reports)} report files")
            return reports
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {e}")
            return {}
    
    def _generate_json_report(self, analysis: ProcessAnalysis, filename: str) -> str:
        """Generate detailed JSON report."""
        
        report_data = {
            "metadata": {
                "report_type": "ADGM Compliance Analysis",
                "generated_at": datetime.now().isoformat(),
                "version": "1.0",
                "system": "ADGM Corporate Agent"
            },
            "process_analysis": {
                "process_type": analysis.process_type.value,
                "documents_uploaded": analysis.documents_uploaded,
                "required_documents": analysis.required_documents,
                "missing_documents": analysis.missing_documents,
                "overall_compliance_score": analysis.overall_compliance_score,
                "processed_at": analysis.processed_at.isoformat(),
                "recommendations": analysis.recommendations
            },
            "document_analyses": [],
            "issues_summary": self._create_issues_summary(analysis),
            "compliance_metrics": self._calculate_compliance_metrics(analysis)
        }
        
        # Add detailed document analyses
        for doc_analysis in analysis.document_analyses:
            doc_data = {
                "filename": doc_analysis.filename,
                "document_type": doc_analysis.document_type.value,
                "type_confidence": doc_analysis.confidence,
                "compliance_score": doc_analysis.compliance_score,
                "word_count": doc_analysis.word_count,
                "processed_at": doc_analysis.processed_at.isoformat(),
                "issues": []
            }
            
            # Add issues
            for issue in doc_analysis.issues:
                issue_data = {
                    "document": issue.document,
                    "section": issue.section,
                    "issue": issue.issue,
                    "severity": issue.severity.value,
                    "suggestion": issue.suggestion,
                    "adgm_reference": issue.adgm_reference,
                    "line_number": issue.line_number
                }
                doc_data["issues"].append(issue_data)
            
            report_data["document_analyses"].append(doc_data)
        
        # Save JSON report
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated JSON report: {filename}")
        return str(output_path)
    
    def _generate_html_report(self, analysis: ProcessAnalysis, filename: str) -> str:
        """Generate HTML report for web viewing."""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADGM Compliance Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; padding: 20px; border-radius: 10px; }}
        .summary {{ background: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .document {{ border: 1px solid #e5e7eb; margin: 15px 0; padding: 15px; border-radius: 8px; }}
        .issue {{ margin: 10px 0; padding: 10px; border-left: 4px solid #fbbf24; background: #fffbeb; }}
        .critical {{ border-left-color: #dc2626; background: #fef2f2; }}
        .high {{ border-left-color: #ea580c; background: #fff7ed; }}
        .medium {{ border-left-color: #d97706; background: #fffbeb; }}
        .low {{ border-left-color: #65a30d; background: #f7fee7; }}
        .score {{ font-size: 24px; font-weight: bold; }}
        .score.good {{ color: #16a34a; }}
        .score.warning {{ color: #d97706; }}
        .score.poor {{ color: #dc2626; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; }}
        th {{ background: #f8fafc; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ ADGM Corporate Agent</h1>
        <h2>Compliance Analysis Report</h2>
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Executive Summary</h2>
        <p><strong>Process Type:</strong> {analysis.process_type.value}</p>
        <p><strong>Documents Analyzed:</strong> {analysis.documents_uploaded}</p>
        <p><strong>Required Documents:</strong> {analysis.required_documents}</p>
        <p><strong>Overall Compliance Score:</strong> 
           <span class="score {self._get_score_class(analysis.overall_compliance_score)}">{analysis.overall_compliance_score}%</span>
        </p>
        
        {self._generate_missing_docs_html(analysis.missing_documents)}
        {self._generate_issues_summary_html(analysis)}
    </div>
    
    <h2>📋 Document Analysis</h2>
    {self._generate_documents_html(analysis.document_analyses)}
    
    <h2>💡 Recommendations</h2>
    <ul>
        {chr(10).join([f"<li>{rec}</li>" for rec in analysis.recommendations])}
    </ul>
    
    <div style="margin-top: 30px; padding: 15px; background: #f8fafc; border-radius: 8px;">
        <p><strong>Disclaimer:</strong> This analysis is provided by the ADGM Corporate Agent AI system. 
        While comprehensive, it should not replace professional legal advice. Always consult with 
        qualified legal professionals for important legal matters.</p>
    </div>
</body>
</html>
"""
        
        # Save HTML report
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML report: {filename}")
        return str(output_path)
    
    def _generate_csv_summary(self, analysis: ProcessAnalysis, filename: str) -> str:
        """Generate CSV summary for spreadsheet analysis."""
        
        import csv
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Document', 'Type', 'Compliance Score', 'Word Count', 
                'Issues Count', 'Critical Issues', 'High Issues', 'Medium Issues', 'Low Issues'
            ])
            
            # Document data
            for doc_analysis in analysis.document_analyses:
                issue_counts = self._count_issues_by_severity(doc_analysis.issues)
                
                writer.writerow([
                    doc_analysis.filename,
                    doc_analysis.document_type.value,
                    doc_analysis.compliance_score,
                    doc_analysis.word_count,
                    len(doc_analysis.issues),
                    issue_counts.get('Critical', 0),
                    issue_counts.get('High', 0),
                    issue_counts.get('Medium', 0),
                    issue_counts.get('Low', 0)
                ])
        
        logger.info(f"Generated CSV summary: {filename}")
        return str(output_path)
    
    def _generate_executive_summary(self, analysis: ProcessAnalysis, filename: str) -> str:
        """Generate executive summary text file."""
        
        summary_lines = [
            "ADGM CORPORATE AGENT - EXECUTIVE SUMMARY",
            "=" * 50,
            "",
            f"Analysis Date: {analysis.processed_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Process Type: {analysis.process_type.value}",
            f"Overall Compliance Score: {analysis.overall_compliance_score}%",
            "",
            "DOCUMENT OVERVIEW:",
            f"- Documents Uploaded: {analysis.documents_uploaded}",
            f"- Required Documents: {analysis.required_documents}",
            f"- Documents Analyzed: {len(analysis.document_analyses)}",
            ""
        ]
        
        # Missing documents
        if analysis.missing_documents:
            summary_lines.extend([
                "MISSING DOCUMENTS:",
                *[f"- {doc}" for doc in analysis.missing_documents],
                ""
            ])
        
        # Issues summary
        all_issues = []
        for doc_analysis in analysis.document_analyses:
            all_issues.extend(doc_analysis.issues)
        
        if all_issues:
            issue_counts = self._count_issues_by_severity(all_issues)
            summary_lines.extend([
                "ISSUES SUMMARY:",
                f"- Total Issues: {len(all_issues)}",
                f"- Critical: {issue_counts.get('Critical', 0)}",
                f"- High: {issue_counts.get('High', 0)}",
                f"- Medium: {issue_counts.get('Medium', 0)}",
                f"- Low: {issue_counts.get('Low', 0)}",
                ""
            ])
        
        # Top recommendations
        if analysis.recommendations:
            summary_lines.extend([
                "KEY RECOMMENDATIONS:",
                *[f"- {rec}" for rec in analysis.recommendations[:5]],
                ""
            ])
        
        summary_lines.extend([
            "NEXT STEPS:",
            "1. Review detailed analysis report",
            "2. Address critical and high-priority issues",
            "3. Upload any missing required documents",
            "4. Consult with legal professionals as needed",
            "",
            "This summary was generated by ADGM Corporate Agent AI system."
        ])
        
        # Save summary
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
        
        logger.info(f"Generated executive summary: {filename}")
        return str(output_path)
    
    def _create_issues_summary(self, analysis: ProcessAnalysis) -> Dict:
        """Create issues summary statistics."""
        
        all_issues = []
        for doc_analysis in analysis.document_analyses:
            all_issues.extend(doc_analysis.issues)
        
        severity_counts = self._count_issues_by_severity(all_issues)
        
        return {
            "total_issues": len(all_issues),
            "by_severity": severity_counts,
            "by_document": {
                doc.filename: len(doc.issues) 
                for doc in analysis.document_analyses
            }
        }
    
    def _calculate_compliance_metrics(self, analysis: ProcessAnalysis) -> Dict:
        """Calculate compliance metrics."""
        
        return {
            "overall_score": analysis.overall_compliance_score,
            "document_scores": {
                doc.filename: doc.compliance_score 
                for doc in analysis.document_analyses
            },
            "completeness_percentage": (
                (analysis.required_documents - len(analysis.missing_documents)) / 
                analysis.required_documents * 100
            ) if analysis.required_documents > 0 else 100,
            "average_document_score": sum(
                doc.compliance_score for doc in analysis.document_analyses
            ) / len(analysis.document_analyses) if analysis.document_analyses else 0
        }
    
    def _count_issues_by_severity(self, issues: List[DocumentIssue]) -> Dict[str, int]:
        """Count issues by severity level."""
        
        counts = {}
        for issue in issues:
            severity = issue.severity.value
            counts[severity] = counts.get(severity, 0) + 1
        
        return counts
    
    def _get_score_class(self, score: float) -> str:
        """Get CSS class for score display."""
        
        if score >= 80:
            return "good"
        elif score >= 60:
            return "warning"
        else:
            return "poor"
    
    def _generate_missing_docs_html(self, missing_docs: List[str]) -> str:
        """Generate HTML for missing documents section."""
        
        if not missing_docs:
            return "<p>✅ <strong>All required documents are present</strong></p>"
        
        html = "<p>⚠️ <strong>Missing Required Documents:</strong></p><ul>"
        for doc in missing_docs:
            html += f"<li>{doc}</li>"
        html += "</ul>"
        
        return html
    
    def _generate_issues_summary_html(self, analysis: ProcessAnalysis) -> str:
        """Generate HTML for issues summary."""
        
        all_issues = []
        for doc_analysis in analysis.document_analyses:
            all_issues.extend(doc_analysis.issues)
        
        if not all_issues:
            return "<p>✅ <strong>No compliance issues found</strong></p>"
        
        issue_counts = self._count_issues_by_severity(all_issues)
        
        html = f"<p><strong>Issues Found:</strong> {len(all_issues)} total</p><ul>"
        for severity in ['Critical', 'High', 'Medium', 'Low']:
            count = issue_counts.get(severity, 0)
            if count > 0:
                html += f"<li><strong>{severity}:</strong> {count}</li>"
        html += "</ul>"
        
        return html
    
    def _generate_documents_html(self, document_analyses: List[DocumentAnalysis]) -> str:
        """Generate HTML for document analyses."""
        
        html = ""
        
        for doc_analysis in document_analyses:
            score_class = self._get_score_class(doc_analysis.compliance_score)
            
            html += f"""
            <div class="document">
                <h3>{doc_analysis.filename}</h3>
                <p><strong>Type:</strong> {doc_analysis.document_type.value}</p>
                <p><strong>Compliance Score:</strong> 
                   <span class="score {score_class}">{doc_analysis.compliance_score}%</span>
                </p>
                <p><strong>Word Count:</strong> {doc_analysis.word_count}</p>
                <p><strong>Issues:</strong> {len(doc_analysis.issues)}</p>
            """
            
            if doc_analysis.issues:
                html += "<h4>Issues Found:</h4>"
                for issue in doc_analysis.issues:
                    severity_class = issue.severity.value.lower()
                    html += f"""
                    <div class="issue {severity_class}">
                        <strong>{issue.severity.value}: {issue.section or 'General'}</strong><br>
                        <strong>Issue:</strong> {issue.issue}<br>
                        {f'<strong>Suggestion:</strong> {issue.suggestion}<br>' if issue.suggestion else ''}
                        {f'<strong>ADGM Reference:</strong> {issue.adgm_reference}<br>' if issue.adgm_reference else ''}
                    </div>
                    """
            else:
                html += "<p>✅ No issues found in this document</p>"
            
            html += "</div>"
        
        return html

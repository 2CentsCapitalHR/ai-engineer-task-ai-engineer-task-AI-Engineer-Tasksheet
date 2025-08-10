import json
import asyncio
from typing import Dict, List
from datetime import datetime
from pathlib import Path

from app.models import DocumentAnalysis, AnalysisReport, DocumentFlag, ComplianceCheck, FlagSeverity
from config import settings

class ReportGenerator:
    def __init__(self):
        pass
    
    async def generate_analysis_report(self, analysis: DocumentAnalysis, document_name: str) -> AnalysisReport:
        """Generate comprehensive analysis report"""
        
        # Count flags by severity
        critical_count = sum(1 for flag in analysis.flags if flag.severity == FlagSeverity.CRITICAL)
        warning_count = sum(1 for flag in analysis.flags if flag.severity == FlagSeverity.WARNING)
        info_count = sum(1 for flag in analysis.flags if flag.severity == FlagSeverity.INFO)
        
        # Determine overall status
        overall_status = self._determine_overall_status(
            analysis.compliance_score, critical_count, warning_count
        )
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            analysis, critical_count, warning_count, info_count
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis)
        
        # Identify missing documents (if applicable)
        missing_documents = analysis.missing_sections
        
        return AnalysisReport(
            document_id=analysis.document_id,
            document_name=document_name,
            document_type=analysis.document_type,
            overall_status=overall_status,
            compliance_score=analysis.compliance_score,
            completeness_score=analysis.completeness_score,
            critical_issues=critical_count,
            warnings=warning_count,
            info_items=info_count,
            flags=analysis.flags,
            compliance_checks=analysis.compliance_checks,
            missing_documents=missing_documents,
            executive_summary=executive_summary,
            recommendations=recommendations
        )
    
    def _determine_overall_status(self, compliance_score: float, critical_count: int, warning_count: int) -> str:
        """Determine overall document status"""
        if critical_count > 0:
            return "CRITICAL_ISSUES"
        elif compliance_score >= 90:
            return "COMPLIANT"
        elif compliance_score >= 70:
            return "PARTIALLY_COMPLIANT"
        elif warning_count > 5:
            return "NEEDS_REVISION"
        else:
            return "NON_COMPLIANT"
    
    def _generate_executive_summary(self, analysis: DocumentAnalysis, critical: int, warnings: int, info: int) -> str:
        """Generate executive summary of analysis"""
        
        doc_type_name = settings.ADGM_DOCUMENT_TYPES.get(
            analysis.document_type.value, {}
        ).get('name', analysis.document_type.value.title())
        
        summary_parts = []
        
        # Document identification
        summary_parts.append(f"Analysis of {doc_type_name} completed on {datetime.now().strftime('%Y-%m-%d %H:%M')}.")
        
        # Compliance overview
        if analysis.compliance_score >= 90:
            summary_parts.append(f"The document demonstrates high compliance (${analysis.compliance_score}%) with ADGM requirements.")
        elif analysis.compliance_score >= 70:
            summary_parts.append(f"The document shows moderate compliance (${analysis.compliance_score}%) with several areas requiring attention.")
        else:
            summary_parts.append(f"The document has significant compliance issues (${analysis.compliance_score}%) that must be addressed.")
        
        # Issue summary
        if critical > 0:
            summary_parts.append(f"CRITICAL: {critical} critical issues identified that require immediate attention.")
        
        if warnings > 0:
            summary_parts.append(f"{warnings} warnings noted that should be addressed for best practice compliance.")
        
        if info > 0:
            summary_parts.append(f"{info} informational items provided for guidance.")
        
        # Completeness assessment
        if analysis.completeness_score >= 95:
            summary_parts.append("Document structure and required sections are complete.")
        elif analysis.completeness_score >= 80:
            summary_parts.append("Document is mostly complete with minor sections missing.")
        else:
            summary_parts.append("Document is missing several required sections and information.")
        
        # Missing sections
        if analysis.missing_sections:
            missing_str = ", ".join(analysis.missing_sections[:3])
            if len(analysis.missing_sections) > 3:
                missing_str += f" and {len(analysis.missing_sections) - 3} others"
            summary_parts.append(f"Key missing sections include: {missing_str}.")
        
        return " ".join(summary_parts)
    
    def _generate_recommendations(self, analysis: DocumentAnalysis) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Critical issues first
        critical_flags = [flag for flag in analysis.flags if flag.severity == FlagSeverity.CRITICAL]
        for flag in critical_flags[:5]:  # Top 5 critical issues
            if flag.suggested_fix:
                recommendations.append(f"CRITICAL: {flag.suggested_fix}")
        
        # Missing sections
        for section in analysis.missing_sections[:3]:  # Top 3 missing sections
            recommendations.append(f"Add required section: {section}")
        
        # Compliance improvements
        non_compliant_checks = [check for check in analysis.compliance_checks if not check.compliant]
        for check in non_compliant_checks[:3]:  # Top 3 compliance issues
            if check.recommendations:
                recommendations.append(check.recommendations[0])
        
        # General improvements
        warning_flags = [flag for flag in analysis.flags if flag.severity == FlagSeverity.WARNING]
        for flag in warning_flags[:2]:  # Top 2 warnings
            if flag.suggested_fix:
                recommendations.append(f"Improve: {flag.suggested_fix}")
        
        # If no specific recommendations, add general ones
        if not recommendations:
            recommendations.extend([
                "Review document for completeness against ADGM requirements",
                "Ensure all mandatory sections are present and properly formatted",
                "Verify compliance with current ADGM regulations"
            ])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def generate_json_report(self, analysis: DocumentAnalysis, document_name: str) -> Dict:
        """Generate detailed JSON report"""
        
        report = await self.generate_analysis_report(analysis, document_name)
        
        return {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0",
                "analyzer_version": "ADGM Corporate Agent v1.0"
            },
            "document_info": {
                "document_id": report.document_id,
                "document_name": report.document_name,
                "document_type": report.document_type.value,
                "analysis_date": report.generated_at.isoformat()
            },
            "summary": {
                "overall_status": report.overall_status,
                "compliance_score": report.compliance_score,
                "completeness_score": report.completeness_score,
                "executive_summary": report.executive_summary
            },
            "issue_counts": {
                "critical_issues": report.critical_issues,
                "warnings": report.warnings,
                "info_items": report.info_items,
                "total_flags": len(report.flags)
            },
            "detailed_findings": {
                "flags": [self._serialize_flag(flag) for flag in report.flags],
                "compliance_checks": [self._serialize_compliance_check(check) for check in report.compliance_checks]
            },
            "missing_elements": {
                "missing_documents": report.missing_documents,
                "missing_sections": analysis.missing_sections
            },
            "recommendations": {
                "prioritized_actions": report.recommendations,
                "next_steps": self._generate_next_steps(report)
            }
        }
    
    def _serialize_flag(self, flag: DocumentFlag) -> Dict:
        """Serialize DocumentFlag to dictionary"""
        return {
            "severity": flag.severity.value,
            "title": flag.title,
            "description": flag.description,
            "location": flag.location,
            "line_number": flag.line_number,
            "suggested_fix": flag.suggested_fix,
            "adgm_reference": flag.adgm_reference
        }
    
    def _serialize_compliance_check(self, check: ComplianceCheck) -> Dict:
        """Serialize ComplianceCheck to dictionary"""
        return {
            "section": check.section,
            "required": check.required,
            "present": check.present,
            "compliant": check.compliant,
            "issues": check.issues,
            "recommendations": check.recommendations
        }
    
    def _generate_next_steps(self, report: AnalysisReport) -> List[str]:
        """Generate next steps based on analysis results"""
        next_steps = []
        
        if report.overall_status == "CRITICAL_ISSUES":
            next_steps.extend([
                "Address all critical issues before proceeding with submission",
                "Review document with legal counsel if needed",
                "Re-submit for analysis after corrections"
            ])
        elif report.overall_status == "NON_COMPLIANT":
            next_steps.extend([
                "Revise document to address compliance gaps",
                "Add missing required sections",
                "Ensure all ADGM requirements are met"
            ])
        elif report.overall_status == "PARTIALLY_COMPLIANT":
            next_steps.extend([
                "Address remaining warnings and issues",
                "Verify compliance improvements",
                "Consider final legal review before submission"
            ])
        else:  # COMPLIANT
            next_steps.extend([
                "Document is ready for submission to ADGM",
                "Keep copy of analysis report for records",
                "Monitor for any regulation updates"
            ])
        
        return next_steps
    
    async def save_report_to_file(self, report_data: Dict, output_path: str) -> bool:
        """Save report to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving report: {str(e)}")
            return False
    
    def generate_summary_stats(self, analyses: List[DocumentAnalysis]) -> Dict:
        """Generate summary statistics for multiple analyses"""
        if not analyses:
            return {}
        
        total_docs = len(analyses)
        avg_compliance = sum(a.compliance_score for a in analyses) / total_docs
        avg_completeness = sum(a.completeness_score for a in analyses) / total_docs
        
        total_flags = sum(len(a.flags) for a in analyses)
        total_critical = sum(len([f for f in a.flags if f.severity == FlagSeverity.CRITICAL]) for a in analyses)
        
        doc_types = {}
        for analysis in analyses:
            doc_type = analysis.document_type.value
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        return {
            "total_documents": total_docs,
            "average_compliance_score": round(avg_compliance, 2),
            "average_completeness_score": round(avg_completeness, 2),
            "total_flags": total_flags,
            "total_critical_issues": total_critical,
            "document_types_processed": doc_types,
            "analysis_period": {
                "start": min(a.created_at for a in analyses).isoformat(),
                "end": max(a.created_at for a in analyses).isoformat()
            }
        }
    
    def format_report_for_display(self, report: AnalysisReport) -> str:
        """Format report for console/text display"""
        
        lines = []
        lines.append("=" * 80)
        lines.append("ADGM CORPORATE AGENT - DOCUMENT ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Document info
        lines.append(f"Document: {report.document_name}")
        lines.append(f"Type: {report.document_type.value.title()}")
        lines.append(f"Analysis Date: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Status: {report.overall_status}")
        lines.append("")
        
        # Scores
        lines.append("COMPLIANCE SCORES")
        lines.append("-" * 20)
        lines.append(f"Overall Compliance: {report.compliance_score}%")
        lines.append(f"Completeness: {report.completeness_score}%")
        lines.append("")
        
        # Issue summary
        lines.append("ISSUE SUMMARY")
        lines.append("-" * 15)
        lines.append(f"Critical Issues: {report.critical_issues}")
        lines.append(f"Warnings: {report.warnings}")
        lines.append(f"Informational: {report.info_items}")
        lines.append("")
        
        # Executive summary
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 18)
        lines.append(report.executive_summary)
        lines.append("")
        
        # Critical flags
        critical_flags = [f for f in report.flags if f.severity == FlagSeverity.CRITICAL]
        if critical_flags:
            lines.append("CRITICAL ISSUES")
            lines.append("-" * 16)
            for i, flag in enumerate(critical_flags, 1):
                lines.append(f"{i}. {flag.title}")
                lines.append(f"   {flag.description}")
                if flag.suggested_fix:
                    lines.append(f"   Fix: {flag.suggested_fix}")
                lines.append("")
        
        # Recommendations
        if report.recommendations:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 15)
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
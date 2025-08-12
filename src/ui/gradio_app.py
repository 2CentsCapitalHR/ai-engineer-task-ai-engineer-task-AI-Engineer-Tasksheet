"""Gradio interface for ADGM Corporate Agent."""

import gradio as gr
import json
import os
from pathlib import Path
from typing import List, Optional, Tuple
import logging

from ..core.processing_engine import ADGMProcessingEngine
from ..rag.vector_store import initialize_vector_store
from ..config import settings

logger = logging.getLogger(__name__)


class ADGMGradioApp:
    """Gradio application for ADGM Corporate Agent."""
    
    def __init__(self):
        self.vector_store = None
        self.processing_engine = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize the processing components."""
        try:
            logger.info("Initializing ADGM Corporate Agent components...")
            
            # Initialize vector store
            self.vector_store = initialize_vector_store()
            
            # Initialize processing engine
            self.processing_engine = ADGMProcessingEngine(self.vector_store)
            
            logger.info("✅ Components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            self.vector_store = None
            self.processing_engine = None
    
    def process_documents(self, files: List, progress=gr.Progress()) -> Tuple[str, str, str, Optional[str]]:
        """Process uploaded documents and return results."""
        
        if not files:
            return "❌ No files uploaded", "", "", None
        
        if not self.processing_engine:
            return "❌ System not properly initialized. Please check configuration.", "", "", None
        
        try:
            progress(0.1, desc="Validating files...")
            
            # Validate files
            file_paths = []
            for file in files:
                if file is None:
                    continue
                
                file_path = file.name if hasattr(file, 'name') else str(file)
                
                if not file_path.lower().endswith('.docx'):
                    return f"❌ Unsupported file format: {file_path}. Only .docx files are supported.", "", "", None
                
                if not os.path.exists(file_path):
                    return f"❌ File not found: {file_path}", "", "", None
                
                file_paths.append(file_path)
            
            if not file_paths:
                return "❌ No valid .docx files found", "", "", None
            
            progress(0.3, desc="Processing documents...")
            
            # Process documents
            result = self.processing_engine.process_documents(file_paths)
            
            if not result.success:
                return f"❌ Processing failed: {result.error_message}", "", "", None
            
            progress(0.8, desc="Generating reports...")
            
            # Generate reports
            summary_report = self._generate_summary_report(result.analysis)
            detailed_report = self._generate_detailed_report(result.analysis)
            json_report = self._generate_json_report(result.analysis)
            
            progress(1.0, desc="Complete!")
            
            # Return results
            return (
                summary_report,
                detailed_report,
                json_report,
                result.output_file_path
            )
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return f"❌ Processing error: {str(e)}", "", "", None
    
    def _generate_summary_report(self, analysis) -> str:
        """Generate a summary report."""
        
        if not analysis:
            return "No analysis available"
        
        # Process identification
        process_info = f"""
# 🏛️ ADGM Corporate Agent - Analysis Summary

## 📋 Process Identification
- **Identified Process**: {analysis.process_type.value}
- **Documents Uploaded**: {analysis.documents_uploaded}
- **Required Documents**: {analysis.required_documents}
- **Overall Compliance Score**: {analysis.overall_compliance_score}%

"""
        
        # Document completeness
        if analysis.missing_documents:
            process_info += f"""
## ⚠️ Missing Documents
{chr(10).join([f"- {doc}" for doc in analysis.missing_documents])}

"""
        else:
            process_info += "## ✅ All Required Documents Present\n\n"
        
        # Issues summary
        all_issues = []
        for doc_analysis in analysis.document_analyses:
            all_issues.extend(doc_analysis.issues)
        
        if all_issues:
            severity_counts = {}
            for issue in all_issues:
                severity = issue.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            process_info += "## 🚨 Issues Summary\n"
            for severity in ['Critical', 'High', 'Medium', 'Low']:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    emoji = {'Critical': '🚨', 'High': '🔴', 'Medium': '🟠', 'Low': '🟡'}[severity]
                    process_info += f"- {emoji} **{severity}**: {count} issue(s)\n"
            
            process_info += "\n"
        else:
            process_info += "## ✅ No Compliance Issues Found\n\n"
        
        # Recommendations
        if analysis.recommendations:
            process_info += "## 💡 Key Recommendations\n"
            for rec in analysis.recommendations[:5]:  # Top 5
                process_info += f"- {rec}\n"
            process_info += "\n"
        
        # Processing info
        process_info += f"""
## 📊 Processing Details
- **Analysis Date**: {analysis.processed_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Documents Analyzed**: {len(analysis.document_analyses)}
- **Total Issues Found**: {len(all_issues)}
"""
        
        return process_info
    
    def _generate_detailed_report(self, analysis) -> str:
        """Generate a detailed report."""
        
        if not analysis:
            return "No analysis available"
        
        report = f"""
# 📄 ADGM Corporate Agent - Detailed Analysis Report

## 🎯 Process Analysis
- **Process Type**: {analysis.process_type.value}
- **Overall Compliance Score**: {analysis.overall_compliance_score}%
- **Documents Uploaded**: {analysis.documents_uploaded}
- **Required Documents**: {analysis.required_documents}

"""
        
        # Document-by-document analysis
        report += "## 📋 Document Analysis\n\n"
        
        for i, doc_analysis in enumerate(analysis.document_analyses, 1):
            report += f"""
### {i}. {doc_analysis.filename}
- **Document Type**: {doc_analysis.document_type.value}
- **Type Confidence**: {doc_analysis.confidence:.1%}
- **Compliance Score**: {doc_analysis.compliance_score}%
- **Word Count**: {doc_analysis.word_count}
- **Issues Found**: {len(doc_analysis.issues)}

"""
            
            if doc_analysis.issues:
                report += "#### 🚨 Issues Identified:\n"
                for j, issue in enumerate(doc_analysis.issues, 1):
                    severity_emoji = {
                        'Low': '🟡', 'Medium': '🟠', 'High': '🔴', 'Critical': '🚨'
                    }
                    emoji = severity_emoji.get(issue.severity.value, '⚠️')
                    
                    report += f"""
**{j}. {emoji} {issue.severity.value} - {issue.section or 'General'}**
- **Issue**: {issue.issue}
- **Suggestion**: {issue.suggestion or 'No specific suggestion provided'}
- **ADGM Reference**: {issue.adgm_reference or 'General ADGM requirements'}

"""
            else:
                report += "#### ✅ No issues found in this document\n\n"
        
        # Missing documents
        if analysis.missing_documents:
            report += "## ⚠️ Missing Required Documents\n\n"
            for doc in analysis.missing_documents:
                report += f"- **{doc}**: Required for {analysis.process_type.value}\n"
            report += "\n"
        
        # Recommendations
        if analysis.recommendations:
            report += "## 💡 Detailed Recommendations\n\n"
            for i, rec in enumerate(analysis.recommendations, 1):
                report += f"{i}. {rec}\n"
            report += "\n"
        
        return report
    
    def _generate_json_report(self, analysis) -> str:
        """Generate a JSON report."""
        
        if not analysis:
            return "{}"
        
        # Convert analysis to dictionary
        report_dict = {
            "process": analysis.process_type.value,
            "documents_uploaded": analysis.documents_uploaded,
            "required_documents": analysis.required_documents,
            "missing_documents": analysis.missing_documents,
            "overall_compliance_score": analysis.overall_compliance_score,
            "processed_at": analysis.processed_at.isoformat(),
            "issues_found": [],
            "document_analyses": [],
            "recommendations": analysis.recommendations
        }
        
        # Add document analyses
        for doc_analysis in analysis.document_analyses:
            doc_dict = {
                "filename": doc_analysis.filename,
                "document_type": doc_analysis.document_type.value,
                "type_confidence": doc_analysis.confidence,
                "compliance_score": doc_analysis.compliance_score,
                "word_count": doc_analysis.word_count,
                "issues": []
            }
            
            # Add issues
            for issue in doc_analysis.issues:
                issue_dict = {
                    "document": issue.document,
                    "section": issue.section,
                    "issue": issue.issue,
                    "severity": issue.severity.value,
                    "suggestion": issue.suggestion,
                    "adgm_reference": issue.adgm_reference
                }
                doc_dict["issues"].append(issue_dict)
                report_dict["issues_found"].append(issue_dict)
            
            report_dict["document_analyses"].append(doc_dict)
        
        return json.dumps(report_dict, indent=2)
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        
        with gr.Blocks(
            title="ADGM Corporate Agent",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
            }
            .header {
                text-align: center;
                padding: 20px;
                background: linear-gradient(90deg, #1e3a8a, #3b82f6);
                color: white;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            """
        ) as interface:
            
            # Header
            gr.HTML("""
            <div class="header">
                <h1>🏛️ ADGM Corporate Agent</h1>
                <h3>AI-Powered Legal Document Intelligence for Abu Dhabi Global Market</h3>
                <p>Upload your legal documents for comprehensive ADGM compliance analysis</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    # File upload section
                    gr.Markdown("## 📁 Document Upload")
                    
                    file_upload = gr.File(
                        label="Upload DOCX Documents",
                        file_count="multiple",
                        file_types=[".docx"]
                    )
                    
                    process_btn = gr.Button(
                        "🔍 Analyze Documents",
                        variant="primary",
                        size="lg"
                    )
                    
                    # System status
                    gr.Markdown("## 📊 System Status")
                    
                    if self.processing_engine:
                        status_text = "✅ System Ready"
                        if self.vector_store:
                            stats = self.vector_store.get_collection_stats()
                            status_text += f"\n📚 Knowledge Base: {stats['total_documents']} documents"
                    else:
                        status_text = "❌ System Not Ready - Check Configuration"
                    
                    gr.Markdown(status_text)
                
                with gr.Column(scale=2):
                    # Results section
                    gr.Markdown("## 📋 Analysis Results")
                    
                    with gr.Tabs():
                        with gr.TabItem("📊 Summary"):
                            summary_output = gr.Markdown(
                                value="Upload documents to see analysis summary..."
                            )
                        
                        with gr.TabItem("📄 Detailed Report"):
                            detailed_output = gr.Markdown(
                                value="Upload documents to see detailed analysis..."
                            )
                        
                        with gr.TabItem("💾 JSON Report"):
                            json_output = gr.Code(
                                value="{}",
                                language="json"
                            )
                        
                        with gr.TabItem("📥 Download"):
                            download_file = gr.File(
                                label="Reviewed Document"
                            )
                            
                            gr.Markdown("""
                            **Download Instructions:**
                            - The reviewed document contains highlighted issues and comments
                            - Comments are inserted directly in the document with ADGM references
                            - Use this document to address compliance issues
                            """)
            
            # Footer
            gr.HTML("""
            <div style="text-align: center; padding: 20px; margin-top: 30px; border-top: 1px solid #e5e7eb;">
                <p><strong>ADGM Corporate Agent</strong> - Powered by AI for Legal Document Intelligence</p>
                <p><em>⚠️ This tool assists with ADGM compliance but does not replace professional legal advice</em></p>
            </div>
            """)
            
            # Event handlers
            process_btn.click(
                fn=self.process_documents,
                inputs=[file_upload],
                outputs=[summary_output, detailed_output, json_output, download_file],
                show_progress=True
            )
        
        return interface


def create_gradio_interface() -> gr.Blocks:
    """Create and return the Gradio interface."""
    app = ADGMGradioApp()
    return app.create_interface()

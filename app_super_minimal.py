"""Super minimal ADGM Corporate Agent - Basic functionality only."""

import gradio as gr
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
import os

# Simple document type detection without heavy dependencies
def identify_document_type(text: str) -> str:
    """Simple document type identification using keywords."""
    text_lower = text.lower()
    
    if any(keyword in text_lower for keyword in ['articles of association', 'articles', 'aoa']):
        return "Articles of Association"
    elif any(keyword in text_lower for keyword in ['memorandum of association', 'memorandum', 'moa']):
        return "Memorandum of Association"
    elif any(keyword in text_lower for keyword in ['board resolution', 'directors resolution', 'resolved that']):
        return "Board Resolution"
    elif any(keyword in text_lower for keyword in ['employment contract', 'employment agreement']):
        return "Employment Contract"
    elif any(keyword in text_lower for keyword in ['ubo declaration', 'beneficial owner']):
        return "UBO Declaration"
    else:
        return "Unknown Document Type"

def check_basic_compliance(text: str, doc_type: str) -> List[Dict]:
    """Basic compliance checking without AI."""
    issues = []
    text_lower = text.lower()
    
    # Check jurisdiction issues
    if any(wrong_jurisdiction in text_lower for wrong_jurisdiction in ['dubai courts', 'uae federal courts', 'abu dhabi courts']):
        if 'adgm' not in wrong_jurisdiction:
            issues.append({
                "section": "Jurisdiction",
                "issue": "Incorrect jurisdiction reference found",
                "severity": "High",
                "suggestion": "Update jurisdiction to reference ADGM Courts"
            })
    
    # Check for missing ADGM reference
    if 'adgm' not in text_lower and doc_type in ["Articles of Association", "Memorandum of Association"]:
        issues.append({
            "section": "ADGM Reference",
            "issue": "No ADGM reference found in document",
            "severity": "Medium",
            "suggestion": "Include proper ADGM references"
        })
    
    # Check for signature sections
    if not any(sig_word in text_lower for sig_word in ['signature', 'signed', 'date']):
        issues.append({
            "section": "Signatures",
            "issue": "No signature section found",
            "severity": "Medium",
            "suggestion": "Add proper signature and date fields"
        })
    
    # Document-specific checks
    if doc_type == "Articles of Association":
        required_sections = ['company name', 'share capital', 'directors']
        for section in required_sections:
            if section not in text_lower:
                issues.append({
                    "section": section.title(),
                    "issue": f"Missing {section} information",
                    "severity": "High",
                    "suggestion": f"Include {section} details in the document"
                })
    
    elif doc_type == "Memorandum of Association":
        required_sections = ['objects', 'liability', 'share capital']
        for section in required_sections:
            if section not in text_lower:
                issues.append({
                    "section": section.title(),
                    "issue": f"Missing {section} information",
                    "severity": "High",
                    "suggestion": f"Include {section} details in the document"
                })
    
    return issues

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except Exception as e:
        return f"Error reading document: {str(e)}"

def check_document_completeness(doc_types: List[str]) -> Dict:
    """Check if required documents are present for incorporation."""
    required_docs = [
        "Articles of Association",
        "Memorandum of Association", 
        "UBO Declaration",
        "Register of Members and Directors",
        "Board Resolution"
    ]
    
    present_docs = []
    missing_docs = []
    
    for required in required_docs:
        found = False
        for uploaded in doc_types:
            if required.lower() in uploaded.lower() or uploaded.lower() in required.lower():
                found = True
                present_docs.append(required)
                break
        
        if not found:
            missing_docs.append(required)
    
    return {
        "total_required": len(required_docs),
        "total_present": len(present_docs),
        "missing_documents": missing_docs,
        "present_documents": present_docs,
        "completeness_percentage": (len(present_docs) / len(required_docs)) * 100
    }

def process_documents_minimal(files):
    """Minimal document processing."""
    if not files:
        return "❌ No files uploaded", "", ""
    
    try:
        results = []
        doc_types = []
        
        for file in files:
            if file is None:
                continue
                
            file_path = file.name if hasattr(file, 'name') else str(file)
            
            if not file_path.lower().endswith('.docx'):
                continue
            
            # Extract text
            text = extract_text_from_docx(file_path)
            
            # Identify document type
            doc_type = identify_document_type(text)
            doc_types.append(doc_type)
            
            # Check compliance
            issues = check_basic_compliance(text, doc_type)
            
            results.append({
                'filename': os.path.basename(file_path),
                'document_type': doc_type,
                'word_count': len(text.split()),
                'issues_count': len(issues),
                'issues': issues
            })
        
        # Check document completeness
        completeness = check_document_completeness(doc_types)
        
        # Create summary
        summary = f"📊 **ADGM Document Analysis Summary**\n\n"
        summary += f"**Documents Processed:** {len(results)}\n"
        summary += f"**Process Identified:** Company Incorporation\n"
        summary += f"**Document Completeness:** {completeness['completeness_percentage']:.1f}%\n"
        summary += f"**Required Documents:** {completeness['total_required']}\n"
        summary += f"**Present Documents:** {completeness['total_present']}\n\n"
        
        if completeness['missing_documents']:
            summary += "**⚠️ Missing Documents:**\n"
            for missing in completeness['missing_documents']:
                summary += f"- {missing}\n"
            summary += "\n"
        
        total_issues = sum(result['issues_count'] for result in results)
        summary += f"**Total Issues Found:** {total_issues}\n\n"
        
        for result in results:
            summary += f"**📄 {result['filename']}**\n"
            summary += f"- Type: {result['document_type']}\n"
            summary += f"- Issues: {result['issues_count']}\n"
            if result['issues']:
                summary += "- Top Issues:\n"
                for issue in result['issues'][:3]:
                    summary += f"  - {issue['severity']}: {issue['issue']}\n"
            summary += "\n"
        
        # Create detailed report
        detailed = "# 🏛️ ADGM Corporate Agent - Detailed Analysis\n\n"
        detailed += f"## 📋 Process Analysis\n"
        detailed += f"- **Process Type:** Company Incorporation\n"
        detailed += f"- **Documents Uploaded:** {len(results)}\n"
        detailed += f"- **Required Documents:** {completeness['total_required']}\n"
        detailed += f"- **Completeness:** {completeness['completeness_percentage']:.1f}%\n\n"
        
        if completeness['missing_documents']:
            detailed += "## ⚠️ Missing Required Documents\n"
            for missing in completeness['missing_documents']:
                detailed += f"- **{missing}**: Required for company incorporation\n"
            detailed += "\n"
        
        detailed += "## 📄 Document Analysis\n\n"
        
        for i, result in enumerate(results, 1):
            detailed += f"### {i}. {result['filename']}\n"
            detailed += f"- **Document Type:** {result['document_type']}\n"
            detailed += f"- **Word Count:** {result['word_count']}\n"
            detailed += f"- **Issues Found:** {result['issues_count']}\n\n"
            
            if result['issues']:
                detailed += "**Issues Identified:**\n"
                for j, issue in enumerate(result['issues'], 1):
                    detailed += f"{j}. **{issue['severity']} - {issue['section']}**\n"
                    detailed += f"   - Issue: {issue['issue']}\n"
                    detailed += f"   - Suggestion: {issue['suggestion']}\n\n"
            else:
                detailed += "✅ No issues found in this document\n\n"
        
        # Create JSON report
        json_report = {
            "process": "Company Incorporation",
            "documents_uploaded": len(results),
            "required_documents": completeness['total_required'],
            "missing_documents": completeness['missing_documents'],
            "completeness_percentage": completeness['completeness_percentage'],
            "document_analyses": results
        }
        
        return summary, detailed, json.dumps(json_report, indent=2)
        
    except Exception as e:
        error_msg = f"❌ Error processing documents: {str(e)}"
        return error_msg, error_msg, "{}"

def create_interface():
    """Create minimal Gradio interface."""
    with gr.Blocks(title="ADGM Corporate Agent - Minimal") as interface:
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🏛️ ADGM Corporate Agent</h1>
            <h3>Minimal Document Analysis System</h3>
            <p>Basic compliance checking for ADGM documents</p>
        </div>
        """)
        
        gr.Markdown("""
        ## 📋 Instructions
        1. Upload your DOCX documents using the file uploader below
        2. Click "Analyze Documents" to process them
        3. Review the results in the tabs below
        
        **Note:** This is a minimal version with basic rule-based checking only.
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                file_upload = gr.File(
                    label="📁 Upload DOCX Documents",
                    file_count="multiple",
                    file_types=[".docx"],
                    height=200
                )
                
                process_btn = gr.Button(
                    "🔍 Analyze Documents", 
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown("""
                ### ✅ System Status
                - **Status:** Ready
                - **Mode:** Minimal (Rule-based only)
                - **Supported:** .docx files
                - **Max Size:** 50MB per file
                """)
            
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.TabItem("📊 Summary"):
                        summary_output = gr.Markdown(
                            value="Upload documents to see analysis summary...",
                            height=400
                        )
                    
                    with gr.TabItem("📄 Detailed Report"):
                        detailed_output = gr.Markdown(
                            value="Upload documents to see detailed analysis...",
                            height=400
                        )
                    
                    with gr.TabItem("💾 JSON Report"):
                        json_output = gr.Code(
                            value="{}",
                            language="json",
                            height=400
                        )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 15px; margin-top: 20px; border-top: 1px solid #e5e7eb; font-size: 0.9em; color: #666;">
            <p><strong>ADGM Corporate Agent - Minimal Version</strong></p>
            <p>⚠️ This tool provides basic compliance checking. Always consult qualified legal professionals.</p>
            <p>🔧 For full AI-powered analysis, ensure sufficient disk space and run the complete version.</p>
        </div>
        """)
        
        # Event handlers
        process_btn.click(
            fn=process_documents_minimal,
            inputs=[file_upload],
            outputs=[summary_output, detailed_output, json_output]
        )
    
    return interface

if __name__ == "__main__":
    print("🏛️ ADGM Corporate Agent - Super Minimal Version")
    print("=" * 50)
    print("Starting minimal application...")
    print("This version uses basic rule-based checking only.")
    print("=" * 50)
    
    app = create_interface()
    app.launch(
        server_name="0.0.0.0", 
        server_port=7860, 
        share=False,
        show_error=True
    )

import streamlit as st
import json
import os
from pathlib import Path
from docx import Document
import io
from typing import List, Dict, Any

# Import our custom modules
from document_processor import DocumentProcessor
from rag_engine import RAGEngine
from compliance_checker import ComplianceChecker
from doc_editor import DocumentEditor

# Page configuration
st.set_page_config(
    page_title="ADGM Corporate Document Review Agent",
    page_icon="⚖️",
    layout="wide"
)

# Initialize session state
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = []
if 'compliance_report' not in st.session_state:
    st.session_state.compliance_report = None

# Load checklist
with open('checklist.json', 'r') as f:
    CHECKLIST = json.load(f)

# Initialize components
@st.cache_resource
def init_components():
    return {
        'processor': DocumentProcessor(),
        'rag': RAGEngine('knowledge_base.json'),
        'checker': ComplianceChecker(),
        'editor': DocumentEditor()
    }

components = init_components()

# Main UI
st.title("🏛️ ADGM Corporate Document Review Agent")
st.markdown("AI-powered compliance checker for ADGM corporate documents")

# Sidebar
with st.sidebar:
    st.header("📋 Configuration")
    
    # Process selection
    process_type = st.selectbox(
        "Select Process Type",
        list(CHECKLIST.keys())
    )
    
    # Upload documents
    st.header("📄 Document Upload")
    uploaded_files = st.file_uploader(
        "Upload .docx files",
        type=['docx'],
        accept_multiple_files=True
    )
    
    if st.button("🔍 Start Review", type="primary"):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                # Process documents
                st.session_state.processed_docs = []
                for file in uploaded_files:
                    doc = components['processor'].process_document(file)
                    st.session_state.processed_docs.append(doc)
                
                # Generate compliance report
                st.session_state.compliance_report = components['checker'].generate_report(
                    st.session_state.processed_docs,
                    process_type,
                    CHECKLIST[process_type]
                )
                
                st.success("Review completed!")

# Main content area
if st.session_state.compliance_report:
    report = st.session_state.compliance_report
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📋 Checklist", "🔍 Issues", "📥 Downloads"])
    
    with tab1:
        st.header("Review Overview")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Documents Uploaded", report['total_documents'])
        with col2:
            st.metric("Required Documents", report['required_documents'])
        with col3:
            st.metric("Missing Documents", len(report['missing_documents']))
        
        if report['missing_documents']:
            st.warning("⚠️ Missing Documents:")
            for doc in report['missing_documents']:
                st.write(f"- {doc}")
    
    with tab2:
        st.header("Document Checklist")
        
        checklist = CHECKLIST[process_type]
        
        # Display checklist with status
        for doc in checklist['required_documents']:
            status = "✅ Uploaded" if doc in [d['type'] for d in report['uploaded_documents']] else "❌ Missing"
            st.write(f"{status} - {doc}")
    
    with tab3:
        st.header("Compliance Issues")
        
        if report['issues']:
            for issue in report['issues']:
                with st.expander(f"{issue['document']} - {issue['section']}"):
                    st.write(f"**Issue:** {issue['description']}")
                    st.write(f"**Severity:** {issue['severity']}")
                    st.write(f"**Suggestion:** {issue['suggestion']}")
                    st.write(f"**ADGM Reference:** {issue['reference']}")
        else:
            st.success("No compliance issues found!")
    
    with tab4:
        st.header("Download Results")
        
        # Download reviewed documents
        for doc in report['uploaded_documents']:
            reviewed_doc = components['editor'].create_reviewed_document(
                doc,
                [i for i in report['issues'] if i['document'] == doc['filename']]
            )
            
            buffer = io.BytesIO()
            reviewed_doc.save(buffer)
            buffer.seek(0)
            
            st.download_button(
                label=f"Download {doc['filename']} (Reviewed)",
                data=buffer,
                file_name=f"reviewed_{doc['filename']}",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        
        # Download JSON report
        json_report = json.dumps(report, indent=2)
        st.download_button(
            label="Download JSON Report",
            data=json_report,
            file_name="compliance_report.json",
            mime="application/json"
        )

else:
    st.info("👋 Upload documents and click 'Start Review' to begin the compliance check.")

# Footer
st.markdown("---")
st.markdown("*Built for ADGM compliance | Powered by AI*")

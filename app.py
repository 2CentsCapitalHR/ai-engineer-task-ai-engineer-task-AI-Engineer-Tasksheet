import streamlit as st
import json
import io
import os
from datetime import datetime
from document_processor import DocumentProcessor
from rag_system import RAGSystem
from compliance_checker import ComplianceChecker
from utils import create_download_link

# Initialize systems
@st.cache_resource
def initialize_systems():
    """Initialize document processor, RAG system, and compliance checker."""
    doc_processor = DocumentProcessor()
    rag_system = RAGSystem()
    compliance_checker = ComplianceChecker(rag_system)
    return doc_processor, rag_system, compliance_checker

def main():
    st.set_page_config(
        page_title="ADGM Corporate Agent",
        page_icon="⚖️",
        layout="wide"
    )
    
    st.title("⚖️ ADGM Corporate Agent")
    st.markdown("*AI-Powered Legal Document Review & Compliance Assistant*")
    
    # Initialize systems
    doc_processor, rag_system, compliance_checker = initialize_systems()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("📋 Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key for document analysis"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ Please provide an OpenAI API key")
            
        st.divider()
        
        # Process selection
        st.header("🎯 Legal Process")
        selected_process = st.selectbox(
            "Select the legal process:",
            [
                "Auto-detect from documents",
                "Company Incorporation",
                "Licensing Application",
                "Employment Contracts",
                "Commercial Agreements",
                "Compliance Review"
            ]
        )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Document Upload")
        
        uploaded_files = st.file_uploader(
            "Upload .docx documents",
            type=['docx'],
            accept_multiple_files=True,
            help="Upload one or more .docx files for review and compliance checking"
        )
        
        if uploaded_files and api_key:
            st.success(f"✅ {len(uploaded_files)} document(s) uploaded")
            
            # Process documents button
            if st.button("🔍 Analyze Documents", type="primary"):
                with st.spinner("Processing documents..."):
                    results = process_documents(
                        uploaded_files, 
                        doc_processor, 
                        compliance_checker, 
                        selected_process
                    )
                    
                    # Store results in session state
                    st.session_state.analysis_results = results
                    st.rerun()
    
    with col2:
        st.header("📊 Analysis Results")
        
        if hasattr(st.session_state, 'analysis_results'):
            display_results(st.session_state.analysis_results)
        else:
            st.info("Upload documents and click 'Analyze Documents' to see results here.")

def process_documents(uploaded_files, doc_processor, compliance_checker, selected_process):
    """Process uploaded documents and return analysis results."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'process_type': selected_process,
        'documents_analyzed': [],
        'compliance_summary': {},
        'overall_issues': [],
        'missing_documents': [],
        'processed_files': []
    }
    
    # Process each uploaded file
    for uploaded_file in uploaded_files:
        try:
            # Parse document
            doc_content = doc_processor.parse_document(uploaded_file)
            
            # Identify document type
            doc_type = doc_processor.identify_document_type(doc_content)
            
            # Analyze for compliance and red flags
            analysis = compliance_checker.analyze_document(doc_content, doc_type)
            
            # Create marked-up document
            marked_doc = doc_processor.create_marked_document(
                uploaded_file, 
                analysis['issues']
            )
            
            doc_result = {
                'filename': uploaded_file.name,
                'document_type': doc_type,
                'issues_found': len(analysis['issues']),
                'high_severity_issues': len([i for i in analysis['issues'] if i['severity'] == 'High']),
                'analysis': analysis,
                'marked_document': marked_doc
            }
            
            results['documents_analyzed'].append(doc_result)
            
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    # Check overall compliance
    if selected_process != "Auto-detect from documents":
        compliance_summary = compliance_checker.check_process_compliance(
            results['documents_analyzed'], 
            selected_process
        )
        results['compliance_summary'] = compliance_summary
        results['missing_documents'] = compliance_summary.get('missing_documents', [])
    
    return results

def display_results(results):
    """Display analysis results in the UI."""
    
    # Overall summary
    st.subheader("📈 Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents Analyzed", len(results['documents_analyzed']))
    with col2:
        total_issues = sum(doc['issues_found'] for doc in results['documents_analyzed'])
        st.metric("Total Issues", total_issues)
    with col3:
        high_severity = sum(doc['high_severity_issues'] for doc in results['documents_analyzed'])
        st.metric("High Severity", high_severity)
    
    # Missing documents alert
    if results.get('missing_documents'):
        st.error("⚠️ Missing Required Documents")
        for missing_doc in results['missing_documents']:
            st.write(f"• {missing_doc}")
    
    # Document-by-document results
    st.subheader("📄 Document Analysis")
    
    for i, doc in enumerate(results['documents_analyzed']):
        with st.expander(f"{doc['filename']} - {doc['document_type']}", expanded=i==0):
            
            # Document metrics
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Document Type:** {doc['document_type']}")
                st.write(f"**Issues Found:** {doc['issues_found']}")
            with col2:
                st.write(f"**High Severity:** {doc['high_severity_issues']}")
                
                # Download marked document
                if doc.get('marked_document'):
                    st.download_button(
                        label="📥 Download Reviewed Document",
                        data=doc['marked_document'],
                        file_name=f"reviewed_{doc['filename']}",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            
            # Issues list
            if doc['analysis']['issues']:
                st.write("**Issues Found:**")
                for issue in doc['analysis']['issues']:
                    severity_color = {
                        'High': '🔴',
                        'Medium': '🟡', 
                        'Low': '🟢'
                    }.get(issue['severity'], '⚪')
                    
                    st.write(f"{severity_color} **{issue['section']}:** {issue['issue']}")
                    if issue.get('suggestion'):
                        st.write(f"   💡 *Suggestion: {issue['suggestion']}*")
                    if issue.get('adgm_reference'):
                        st.write(f"   📚 *Reference: {issue['adgm_reference']}*")
            else:
                st.success("✅ No issues found in this document")
    
    # Download JSON report
    st.subheader("📋 Export Report")
    
    # Create downloadable JSON report
    json_report = json.dumps(results, indent=2, default=str)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 Download JSON Report",
            data=json_report,
            file_name=f"adgm_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        if st.button("🔄 Clear Results"):
            if hasattr(st.session_state, 'analysis_results'):
                del st.session_state.analysis_results
            st.rerun()

if __name__ == "__main__":
    main()

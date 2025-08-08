import streamlit as st
import json
import io
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from document_processor import DocumentProcessor
from rag_system import RAGSystem
from compliance_checker import ComplianceChecker
from utils import create_download_link
import time
import threading

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="ADGM Corporate Agent",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
def init_session_state():
    """Initialize session state variables to prevent KeyError issues."""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = [
            {"date": "2025-01-15", "documents": 12, "issues": 8, "score": 85},
            {"date": "2025-01-10", "documents": 8, "issues": 15, "score": 72},
            {"date": "2025-01-05", "documents": 5, "issues": 3, "score": 95}
        ]
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {'is_processing': False, 'progress': 0, 'message': ''}
    if 'uploaded_files_hash' not in st.session_state:
        st.session_state.uploaded_files_hash = None

# Optimized system initialization with proper caching
@st.cache_resource(show_spinner=False)
def initialize_systems():
    """Initialize document processor, RAG system, and compliance checker."""
    try:
        doc_processor = DocumentProcessor()
        rag_system = RAGSystem()
        compliance_checker = ComplianceChecker(rag_system)
        return doc_processor, rag_system, compliance_checker
    except Exception as e:
        st.error(f"Failed to initialize systems: {str(e)}")
        return None, None, None

# Optimized CSS - moved to function to prevent re-execution
@st.cache_data
def get_custom_css():
    """Return custom CSS for styling."""
    return """
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin: 0.8rem 0;
        text-align: center;
    }
    .sidebar-section {
        background: #f8fafc;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.8rem 0;
    }
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }
    .issue-card {
        margin: 0.3rem 0;
        padding: 0.4rem;
        border-radius: 4px;
        border-left: 3px solid;
    }
    .issue-high { border-color: #dc2626; background: #fee2e2; }
    .issue-medium { border-color: #d97706; background: #fef3c7; }
    .issue-low { border-color: #16a34a; background: #dcfce7; }
    </style>
    """

def render_sidebar():
    """Render optimized sidebar content."""
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        
        # API Configuration
        st.markdown("### 🔑 API Configuration")
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=os.getenv("GEMINI_API_KEY", ""),
            help="Enter your Gemini API key"
        )
        
        # Update environment variable only if changed
        if api_key and api_key != os.getenv("GEMINI_API_KEY", ""):
            os.environ["GEMINI_API_KEY"] = api_key
        
        # Status indicator
        if api_key:
            st.success("✅ API Key Active", icon="✅")
        else:
            st.error("⚠️ API Key Required", icon="⚠️")
        
        st.divider()
        
        # Process Selection
        st.markdown("### 🎯 Process Type")
        selected_process = st.selectbox(
            "Select process:",
            [
                "Auto-detect from documents",
                "Company Incorporation",
                "Licensing Application", 
                "Employment Contracts",
                "Commercial Agreements",
                "Compliance Review"
            ],
            help="Choose the legal process"
        )
        
        st.divider()
        
        # Quick Analytics (optimized)
        st.markdown("### 📊 Analytics")
        
        if st.session_state.analysis_history:
            total_docs = sum(h["documents"] for h in st.session_state.analysis_history)
            avg_score = sum(h["score"] for h in st.session_state.analysis_history) // len(st.session_state.analysis_history)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📄 Docs", total_docs)
            with col2:
                st.metric("🎯 Score", f"{avg_score}%")
        
        st.divider()
        
        # Settings
        st.markdown("### ⚙️ Settings")
        analysis_depth = st.slider("Analysis Depth", 1, 5, 3)
        auto_download = st.checkbox("Auto-download")
        include_suggestions = st.checkbox("AI suggestions", value=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return api_key, selected_process, analysis_depth, auto_download, include_suggestions

def create_file_hash(uploaded_files):
    """Create a hash of uploaded files to detect changes."""
    if not uploaded_files:
        return None
    return hash(tuple((f.name, f.size) for f in uploaded_files))

def render_upload_section(api_key):
    """Render the file upload section."""
    st.markdown("""
    <div class="feature-card">
        <h3>📤 Smart Document Upload & Analysis</h3>
        <p>Upload multiple documents for ADGM compliance review</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Drop your .docx files here or click to browse",
        type=['docx'],
        accept_multiple_files=True,
        help="Supports: Articles, Contracts, Board Resolutions"
    )
    
    if uploaded_files:
        # Check if files have changed
        current_hash = create_file_hash(uploaded_files)
        files_changed = current_hash != st.session_state.uploaded_files_hash
        
        if files_changed:
            st.session_state.uploaded_files_hash = current_hash
            # Clear previous results if files changed
            st.session_state.analysis_results = None
        
        # Optimized file preview
        with st.expander(f"📋 {len(uploaded_files)} Document{'s' if len(uploaded_files) > 1 else ''} Uploaded", expanded=False):
            for file in uploaded_files[:5]:  # Limit display to first 5 files
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"📄 **{file.name}**")
                with col2:
                    st.write(f"{file.size:,} bytes")
            
            if len(uploaded_files) > 5:
                st.write(f"... and {len(uploaded_files) - 5} more files")
        
        # Analysis options (simplified)
        col1, col2 = st.columns(2)
        with col1:
            priority_mode = st.checkbox("⚡ Priority Analysis")
        with col2:
            detailed_report = st.checkbox("📈 Detailed Report", value=True)
        
        # Analysis button
        if api_key:
            if not st.session_state.processing_status['is_processing']:
                if st.button(
                    f"🔍 Analyze {len(uploaded_files)} Document{'s' if len(uploaded_files) > 1 else ''}", 
                    type="primary",
                    use_container_width=True
                ):
                    # Set processing state
                    st.session_state.processing_status['is_processing'] = True
                    st.rerun()
            else:
                # Show processing status
                st.info(f"🔄 Processing... {st.session_state.processing_status['message']}")
                progress = st.progress(st.session_state.processing_status['progress'])
        else:
            st.error("⚠️ Please configure your API key in the sidebar")
    else:
        # Instructions when no files uploaded
        st.info("📚 Upload your legal documents to begin ADGM compliance analysis")
        
        st.markdown("""
        **What we analyze:**
        - ⚖️ ADGM Compliance
        - 🚩 Risk Detection  
        - 📋 Completeness
        - 🎯 Regulatory Alignment
        """)
    
    return uploaded_files

def process_documents_optimized(uploaded_files, doc_processor, compliance_checker, selected_process):
    """Optimized document processing function."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'process_type': selected_process,
        'documents_analyzed': [],
        'compliance_summary': {},
        'missing_documents': [],
        'processing_time': 0
    }
    
    start_time = time.time()
    total_files = len(uploaded_files)
    
    try:
        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress = int((i / total_files) * 90) + 10
            st.session_state.processing_status['progress'] = progress
            st.session_state.processing_status['message'] = f"Analyzing {uploaded_file.name}..."
            
            # Process document
            doc_content = doc_processor.parse_document(uploaded_file)
            doc_type = doc_processor.identify_document_type(doc_content)
            analysis = compliance_checker.analyze_document(doc_content, doc_type)
            
            # Create result
            doc_result = {
                'filename': uploaded_file.name,
                'document_type': doc_type,
                'issues_found': len(analysis['issues']),
                'high_severity_issues': len([i for i in analysis['issues'] if i['severity'] == 'High']),
                'medium_severity_issues': len([i for i in analysis['issues'] if i['severity'] == 'Medium']),
                'low_severity_issues': len([i for i in analysis['issues'] if i['severity'] == 'Low']),
                'compliance_score': analysis.get('compliance_score', 85),  # Default score
                'analysis': analysis,
                'file_size': uploaded_file.size,
                'processed_at': datetime.now().isoformat()
            }
            
            results['documents_analyzed'].append(doc_result)
        
        # Final processing
        st.session_state.processing_status['progress'] = 95
        st.session_state.processing_status['message'] = "Generating compliance summary..."
        
        if selected_process != "Auto-detect from documents":
            compliance_summary = compliance_checker.check_process_compliance(
                results['documents_analyzed'], 
                selected_process
            )
            results['compliance_summary'] = compliance_summary
            results['missing_documents'] = compliance_summary.get('missing_documents', [])
        
        results['processing_time'] = round(time.time() - start_time, 2)
        
        # Complete processing
        st.session_state.processing_status['progress'] = 100
        st.session_state.processing_status['message'] = "Analysis complete!"
        st.session_state.processing_status['is_processing'] = False
        
        return results
        
    except Exception as e:
        st.session_state.processing_status['is_processing'] = False
        st.error(f"Processing error: {str(e)}")
        return None

def render_results_optimized(results):
    """Render analysis results with optimized performance."""
    if not results or not results.get('documents_analyzed'):
        return
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_issues = sum(doc['issues_found'] for doc in results['documents_analyzed'])
    high_severity = sum(doc['high_severity_issues'] for doc in results['documents_analyzed'])
    avg_score = sum(doc['compliance_score'] for doc in results['documents_analyzed']) / len(results['documents_analyzed'])
    
    with col1:
        st.metric("📄 Documents", len(results['documents_analyzed']))
    with col2:
        st.metric("⚠️ Issues", total_issues)
    with col3:
        st.metric("🎯 Avg Score", f"{avg_score:.0f}%")
    with col4:
        st.metric("⏱️ Time", f"{results.get('processing_time', 0)}s")
    
    # Compliance gauge (simplified)
    if avg_score > 0:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = avg_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Compliance Score"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#3b82f6"},
                'steps': [
                    {'range': [0, 60], 'color': "#fee2e2"},
                    {'range': [60, 85], 'color': "#fef3c7"},
                    {'range': [85, 100], 'color': "#dcfce7"}
                ]
            }
        ))
        fig.update_layout(height=200, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Missing documents alert
    if results.get('missing_documents'):
        st.error("⚠️ **Missing Required Documents**")
        for missing_doc in results['missing_documents']:
            st.write(f"• {missing_doc}")
    
    # Document results (optimized display)
    st.markdown("### 📄 Document Analysis")
    
    for doc in results['documents_analyzed']:
        with st.expander(
            f"{doc['filename']} - Score: {doc['compliance_score']}% ({doc['issues_found']} issues)",
            expanded=False
        ):
            # Overview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Type:** {doc['document_type']}")
            with col2:
                st.write(f"**Issues:** {doc['issues_found']}")
            with col3:
                st.write(f"**Size:** {doc['file_size']:,} bytes")
            
            # Issues (optimized display)
            if doc['analysis']['issues']:
                st.markdown("**Issues Found:**")
                for issue in doc['analysis']['issues'][:10]:  # Limit to first 10 issues
                    severity_class = f"issue-{issue['severity'].lower()}"
                    st.markdown(f"""
                    <div class="issue-card {severity_class}">
                        <strong>{issue['section']}</strong><br>
                        {issue['issue']}<br>
                        <em>{issue.get('suggestion', '')}</em>
                    </div>
                    """, unsafe_allow_html=True)
                
                if len(doc['analysis']['issues']) > 10:
                    st.info(f"... and {len(doc['analysis']['issues']) - 10} more issues")
            else:
                st.success("✅ No issues found")
    
    # Export section
    st.markdown("### 📥 Export")
    col1, col2 = st.columns(2)
    
    with col1:
        json_report = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📄 Download Report",
            data=json_report,
            file_name=f"adgm_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        if st.button("🔄 Clear Results"):
            st.session_state.analysis_results = None
            st.session_state.processing_status['is_processing'] = False
            st.rerun()

def render_dashboard_placeholder():
    """Render dashboard when no analysis is available."""
    st.markdown("""
    <div class="main-header">
        <h2>🚀 Welcome to ADGM Corporate Agent</h2>
        <p>Your intelligent legal compliance assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🔍 Smart Analysis</h4>
            <p>AI-powered document review</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>⚖️ Compliance</h4>
            <p>ADGM regulation verification</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>📊 Reports</h4>
            <p>Detailed compliance analysis</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application function."""
    # Initialize session state
    init_session_state()
    
    # Apply CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ ADGM Corporate Agent</h1>
        <p>Professional AI-Powered Legal Document Review & Compliance Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize systems with error handling
    doc_processor, rag_system, compliance_checker = initialize_systems()
    if not all([doc_processor, rag_system, compliance_checker]):
        st.error("Failed to initialize systems. Please refresh the page.")
        return
    
    # Sidebar
    api_key, selected_process, analysis_depth, auto_download, include_suggestions = render_sidebar()
    
    # Main content layout
    if st.session_state.analysis_results is None:
        render_dashboard_placeholder()
    
    # Two-column layout
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        uploaded_files = render_upload_section(api_key)
        
        # Handle processing
        if (st.session_state.processing_status['is_processing'] and 
            uploaded_files and api_key and 
            st.session_state.analysis_results is None):
            
            with st.spinner("Processing documents..."):
                results = process_documents_optimized(
                    uploaded_files, doc_processor, compliance_checker, selected_process
                )
                
                if results:
                    st.session_state.analysis_results = results
                    st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Analysis Dashboard</h3>
            <p>Real-time compliance insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            render_results_optimized(st.session_state.analysis_results)
        else:
            st.info("📋 Upload documents to see analysis results here")

if __name__ == "__main__":
    main()
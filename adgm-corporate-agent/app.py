import streamlit as st
import os
import tempfile
import json
from docx.shared import RGBColor
from modules.document_parser import DocumentParser
from modules.document_checker import DocumentChecker
from modules.comment_inserter import CommentInserter
from modules.report_generator import ReportGenerator
import config

def main():
    """Main application function"""
    # Set page config
    st.set_page_config(
        page_title="ADGM Corporate Agent",
        page_icon="⚖️",
        layout="wide"
    )
    
    # Validate configuration on startup
    try:
        config.validate_config()
    except ValueError as e:
        st.error(f"Configuration Error: {e}")
        st.info("Please check your .env file and ensure OPENAI_API_KEY is set correctly.")
        st.stop()
    except Exception as e:
        st.error(f"System Error: {e}")
        st.stop()
    
    st.title("⚖️ ADGM Corporate Agent")
    st.subheader("AI-Powered Legal Document Review & Compliance Checker")
    
    # Load process checklists
    try:
        with open('templates/checklists.json', 'r') as f:
            checklists = json.load(f)
    except Exception as e:
        st.error(f"Error loading process checklists: {e}")
        st.stop()
    
    # Initialize components with error handling
    try:
        parser = DocumentParser()
        checker = DocumentChecker()
        comment_inserter = CommentInserter()
        report_generator = ReportGenerator()
        st.success("✅ All components initialized successfully")
    except Exception as e:
        st.error(f"❌ Error initializing components: {e}")
        st.stop()
    
    # Process Selection Section
    st.header("🎯 Select ADGM Process Type")
    
    # Create process options with descriptions
    process_options = {}
    for process_key, process_data in checklists.items():
        process_name = process_data['name']
        process_desc = process_data['description']
        required_count = len(process_data['required_documents'])
        optional_count = len(process_data.get('optional_documents', []))
        
        display_text = f"{process_name} ({required_count} required docs"
        if optional_count > 0:
            display_text += f", {optional_count} optional"
        display_text += ")"
        
        process_options[display_text] = process_key
    
    # Process selection dropdown
    selected_process_display = st.selectbox(
        "Choose the ADGM process you want to prepare documents for:",
        options=list(process_options.keys()),
        help="Select the specific legal process to get tailored document requirements"
    )
    
    selected_process = process_options[selected_process_display]
    process_info = checklists[selected_process]
    
    # Display selected process information
    st.info(f"📋 **{process_info['name']}**: {process_info['description']}")
    
    # Show process requirements
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Required Documents")
        required_docs = process_info['required_documents']
        for i, doc in enumerate(required_docs, 1):
            st.write(f"{i}. **{doc.replace('_', ' ').title()}**")
    
    with col2:
        st.subheader("📋 Optional Documents")
        optional_docs = process_info.get('optional_documents', [])
        if optional_docs:
            for i, doc in enumerate(optional_docs, 1):
                st.write(f"{i}. *{doc.replace('_', ' ').title()}*")
        else:
            st.write("*No optional documents for this process*")
    
    # File upload section
    st.header("📄 Upload Documents")
    
    # Show process-specific guidance
    with st.expander(f"📖 {process_info['name']} Guidance"):
        st.markdown(f"""
        **Process Overview:** {process_info['description']}
        
        **Required Documents ({len(required_docs)}):**
        """)
        for doc in required_docs:
            st.write(f"- {doc.replace('_', ' ').title()}")
        
        if optional_docs:
            st.markdown(f"\n**Optional Documents ({len(optional_docs)}):**")
            for doc in optional_docs:
                st.write(f"- {doc.replace('_', ' ').title()}")
        
        # Add process-specific keywords for better recognition
        keywords = process_info.get('process_keywords', [])
        if keywords:
            st.markdown(f"\n**Keywords to include in documents:** {', '.join(keywords)}")
    
    uploaded_files = st.file_uploader(
        f"Upload your {process_info['name']} documents (.docx or .pdf format)",
        type=['docx', 'pdf'],
        accept_multiple_files=True,
        help=f"Upload documents for {process_info['name']} process. Required: {len(required_docs)} documents"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} document(s) uploaded successfully")
        
        # Show uploaded files with their types
        st.write("**Uploaded Files:**")
        for file in uploaded_files:
            file_type = "📄 PDF" if file.name.endswith('.pdf') else "📝 Word"
            st.write(f"• {file_type} {file.name} ({file.size} bytes)")
        
        # Show progress towards completion
        progress_text = f"📊 **Progress:** {len(uploaded_files)}/{len(required_docs)} required documents uploaded"
        if len(uploaded_files) >= len(required_docs):
            st.success(progress_text + " ✅ Complete!")
        elif len(uploaded_files) >= len(required_docs) * 0.8:
            st.warning(progress_text + " ⚠️ Almost there!")
        else:
            st.info(progress_text + " 📋 More documents needed")
        
        if st.button("🔍 Analyze Documents", type="primary"):
            with st.spinner(f"🔄 Analyzing {process_info['name']} documents..."):
                try:
                    # Process documents with selected process context
                    documents = []
                    temp_files = []
                    
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing {uploaded_file.name}...")
                        progress_bar.progress((i + 1) / len(uploaded_files))
                        
                        # Save uploaded file temporarily
                        file_extension = os.path.splitext(uploaded_file.name)[1]
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
                        temp_file.write(uploaded_file.read())
                        temp_file.close()
                        temp_files.append(temp_file.name)
                        
                        # Parse document
                        doc_analysis = parser.parse_document(temp_file.name)
                        doc_analysis['filename'] = uploaded_file.name
                        documents.append(doc_analysis)
                    
                    status_text.text("Checking completeness against selected process...")
                    
                    # Filter out documents with errors
                    valid_documents = [doc for doc in documents if 'error' not in doc]
                    
                    if not valid_documents:
                        st.error("❌ Could not process any documents. Please check file formats and content.")
                        return
                    
                    # Use selected process for completeness checking
                    completeness = checker.check_completeness(valid_documents, selected_process)
                    
                    status_text.text("Detecting red flags and compliance issues...")
                    
                    # Detect red flags for each document
                    for i, doc in enumerate(documents):
                        if 'error' not in doc:
                            red_flags = checker.detect_red_flags(doc)
                            documents[i]['red_flags'] = red_flags
                        else:
                            documents[i]['red_flags'] = [{
                                'type': 'document_error',
                                'severity': 'high',
                                'message': doc.get('error', 'Unknown error'),
                                'suggestion': 'Please check the document format and try again'
                            }]
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display results with process context
                    display_results(documents, completeness, selected_process, process_info)
                    
                    # Generate reports and modified documents
                    generate_outputs(documents, completeness, temp_files, 
                                   comment_inserter, report_generator, uploaded_files, process_info)
                    
                except Exception as e:
                    st.error(f"❌ Error during analysis: {e}")
                    st.info("Please check your files and try again.")
                finally:
                    # Cleanup temp files
                    for temp_file in temp_files:
                        try:
                            if os.path.exists(temp_file):
                                os.unlink(temp_file)
                        except Exception as e:
                            st.warning(f"Could not delete temporary file: {e}")
    else:
        # Show process-specific examples when no files uploaded
        st.info(f"👆 Please upload your {process_info['name']} documents to get started")
        
        # Process-specific examples
        if selected_process == "company_incorporation":
            st.markdown("""
            **📋 Company Incorporation Example Documents:**
            - Articles of Association with ADGM jurisdiction
            - Memorandum of Association with business objects
            - Board Resolution for incorporation decisions
            - UBO Declaration with beneficial ownership details
            - Register of Members with shareholder information
            """)
        elif selected_process == "licensing":
            st.markdown("""
            **📋 Business Licensing Example Documents:**
            - License Application with business details
            - Business Plan with operational strategy
            - Compliance Manual with risk procedures
            """)
        elif selected_process == "employment_setup":
            st.markdown("""
            **📋 Employment Setup Example Documents:**
            - Employment Contract with ADGM jurisdiction
            - HR Policy with employee procedures
            - Data Protection Policy with privacy controls
            """)

def display_results(documents, completeness, process_key, process_info):
    """Display analysis results with process context"""
    st.header("📊 Analysis Results")
    
    # Process-specific header
    st.success(f"🎯 **Analysis for:** {process_info['name']}")
    
    # Enhanced metrics with process context
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Selected Process", process_info['name'])
    with col2:
        st.metric("Documents Uploaded", completeness.get('documents_uploaded', 0))
    with col3:
        st.metric("Required Documents", completeness.get('required_documents', 0))
    with col4:
        completion_rate = completeness.get('completion_rate', 0) * 100
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Process-specific status indicator
    if completion_rate >= 100:
        st.success(f"🎉 All required documents for {process_info['name']} are present!")
    elif completion_rate >= 80:
        st.warning(f"⚠️ {process_info['name']} is almost complete - only a few documents missing")
    elif completion_rate >= 50:
        st.warning(f"📋 {process_info['name']} is partially complete - several documents needed")
    elif completion_rate > 0:
        st.error(f"❌ Many required documents for {process_info['name']} are missing")
    else:
        st.info(f"ℹ️ Could not identify documents for {process_info['name']} process")
    
    # Missing documents with process context
    missing_docs = completeness.get('missing_documents', [])
    if missing_docs:
        st.subheader(f"📋 Missing Required Documents for {process_info['name']}")
        
        cols = st.columns(min(3, len(missing_docs)))
        for i, missing_doc in enumerate(missing_docs):
            with cols[i % len(cols)]:
                st.write(f"❌ **{missing_doc.replace('_', ' ').title()}**")
    
    # Rest of the display_results function remains the same...
    # (Document analysis details, issues summary, etc.)
    
    # Document analysis with enhanced display
    st.subheader("📋 Document Analysis Details")
    
    # Summary statistics
    total_issues = sum(len(doc.get('red_flags', [])) for doc in documents)
    high_severity = sum(1 for doc in documents for flag in doc.get('red_flags', []) if flag.get('severity') == 'high')
    medium_severity = sum(1 for doc in documents for flag in doc.get('red_flags', []) if flag.get('severity') == 'medium')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Issues Found", total_issues)
    with col2:
        st.metric("High Severity Issues", high_severity)
    with col3:
        st.metric("Medium Severity Issues", medium_severity)
    
    # Individual document analysis
    for doc in documents:
        doc_type = doc.get('document_type', 'unknown').replace('_', ' ').title()
        red_flags = doc.get('red_flags', [])
        
        # Color code based on issues
        if 'error' in doc:
            status_color = "❌"
            status_text = "Error"
        elif red_flags:
            high_issues = [f for f in red_flags if f.get('severity') == 'high']
            if high_issues:
                status_color = "🔴"
                status_text = "High Issues"
            else:
                status_color = "🟡"
                status_text = "Minor Issues"
        else:
            status_color = "🟢"
            status_text = "No Issues"
        
        with st.expander(f"{status_color} {doc['filename']} ({doc_type}) - {status_text}"):
            if 'error' in doc:
                st.error(f"❌ **Error:** {doc['error']}")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**📄 Document Information:**")
                    st.write(f"• **Type:** {doc_type}")
                    st.write(f"• **Word Count:** {doc.get('word_count', 'N/A')}")
                    st.write(f"• **Paragraphs:** {doc.get('paragraph_count', 'N/A')}")
                    
                    # Show extracted sections if available
                    sections = doc.get('sections', {})
                    if sections:
                        st.write("**🔍 Extracted Information:**")
                        for key, value in sections.items():
                            if value:
                                display_value = value[:100] + "..." if len(value) > 100 else value
                                st.write(f"• **{key.replace('_', ' ').title()}:** {display_value}")
                
                with col2:
                    st.write("**🚨 Issues Found:**")
                    if red_flags:
                        for flag in red_flags:
                            severity = flag.get('severity', 'medium').upper()
                            severity_icon = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
                            
                            st.write(f"{severity_icon} **{severity}:** {flag.get('message', 'No message')}")
                            if flag.get('suggestion'):
                                st.write(f"   💡 *Suggestion: {flag['suggestion']}*")
                    else:
                        st.success("✅ No major issues detected")

def generate_outputs(documents, completeness, temp_files, comment_inserter, 
                    report_generator, uploaded_files, process_info):
    """Generate output files with process context"""
    st.header("📤 Download Results")
    
    # Enhanced analysis results with process context
    analysis_results = {
        'process': completeness.get('process', 'unknown'),
        'process_name': process_info['name'],
        'process_description': process_info['description'],
        'documents_uploaded': completeness.get('documents_uploaded', 0),
        'required_documents': completeness.get('required_documents', 0),
        'missing_documents': completeness.get('missing_documents', []),
        'completion_rate': completeness.get('completion_rate', 0),
        'document_analyses': documents
    }
    
    try:
        report = report_generator.generate_json_report(analysis_results)
        
        # Create two columns for downloads
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Analysis Report")
            st.download_button(
                label=f"📊 Download {process_info['name']} Report",
                data=json.dumps(report, indent=2),
                file_name=f"adgm_{completeness.get('process', 'unknown')}_analysis_report.json",
                mime="application/json",
                help=f"Download detailed analysis report for {process_info['name']} process"
            )
        
        with col2:
            st.subheader("📄 Reviewed Documents")
            
            # Rest of the generate_outputs function remains similar...
            # (Document generation and download logic)
            
            # Generate reviewed documents
            documents_with_issues = [doc for doc in documents if doc.get('red_flags') and 'error' not in doc]
            
            if documents_with_issues:
                for i, (doc, temp_file, uploaded_file) in enumerate(zip(documents, temp_files, uploaded_files)):
                    red_flags = doc.get('red_flags', [])
                    if red_flags and 'error' not in doc:
                        try:
                            # Determine output file extension
                            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                            if file_extension == '.pdf':
                                output_path = f"reviewed_{os.path.splitext(uploaded_file.name)[0]}_report.docx"
                                label_text = f"📄 {uploaded_file.name} (Review Report)"
                            else:
                                output_path = f"reviewed_{uploaded_file.name}"
                                label_text = f"📄 {uploaded_file.name} (Reviewed)"
                            
                            # Create reviewed document
                            result_path = comment_inserter.add_comments_to_document(temp_file, red_flags, output_path)
                            
                            if result_path and os.path.exists(result_path):
                                # Read the reviewed document
                                with open(result_path, 'rb') as f:
                                    reviewed_content = f.read()
                                
                                st.download_button(
                                    label=label_text,
                                    data=reviewed_content,
                                    file_name=os.path.basename(output_path),
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    help=f"Download review for {uploaded_file.name} with inline comments and suggestions"
                                )
                                
                                # Cleanup
                                os.unlink(result_path)
                            else:
                                st.error(f"Could not create reviewed version of {uploaded_file.name}")
                                
                        except Exception as e:
                            st.error(f"Error creating reviewed version of {uploaded_file.name}: {e}")
            else:
                st.info("No documents required review (no issues found or documents had errors)")
    
    except Exception as e:
        st.error(f"Error generating outputs: {e}")
    
    # Show process-specific summary
    st.subheader(f"📈 {process_info['name']} Summary")
    
    completion_rate = completeness.get('completion_rate', 0) * 100
    
    if completion_rate >= 100:
        st.balloons()  # Celebrate complete submissions!
        st.success(f"🎉 Congratulations! Your {process_info['name']} document set is complete for ADGM submission.")
    else:
        missing_count = len(completeness.get('missing_documents', []))
        if missing_count > 0:
            st.info(f"📋 You need {missing_count} more document(s) to complete your {process_info['name']} application.")

if __name__ == "__main__":
    main()

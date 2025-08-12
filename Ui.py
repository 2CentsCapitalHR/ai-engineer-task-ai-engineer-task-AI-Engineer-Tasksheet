import streamlit as st
import json
from Src.main import process_documents

st.title("📑 Document Compliance Checker")

uploaded_files = st.file_uploader(
    "Upload your documents",
    type=["docx", "pdf"],
    accept_multiple_files=True
)

if st.button("Run Compliance Check") and uploaded_files:
    with st.spinner("Processing documents..."):
        report = process_documents(uploaded_files)

    st.success("✅ Compliance check completed!")


    formatted_report = []
    for category in report:
        formatted_report.append({
            "process": category["process"],
            "documents_uploaded": category["documents_uploaded"],
            "required_documents": category["required_documents"],
            "missing_document": category["missing_document"] if category["missing_document"] else [],
            "issues_found": category["issues_found"] if category["issues_found"] else []
        })

    
    st.subheader("📄 JSON Report")
    st.json(formatted_report)

    # Download JSON
    json_report = json.dumps(formatted_report, indent=4)
    st.download_button(
        label="📥 Download JSON Report",
        data=json_report,
        file_name="compliance_report.json",
        mime="application/json"
    )

# main.py

import streamlit as st
from utils import extract_text, detect_document_type, compare_with_checklist, insert_comment
from llm_checker import check_legal_issues
import tempfile
import json
import os

st.title("ADGM-Compliant Corporate Agent")

# Step 1: Select ADGM process
process = st.selectbox(
    "Select ADGM process:",
    ["Company Incorporation", "Licensing"]
)

# Step 2: Upload files
uploaded_files = st.file_uploader(
    "Upload one or more .docx files:",
    type="docx",
    accept_multiple_files=True
)

if uploaded_files and st.button("Process Documents"):
    all_doc_types = []
    summary = {
        "process": process,
        "documents_uploaded": len(uploaded_files),
        "required_documents": [],
        "missing_documents": [],
        "issues_found": []
    }
    reviewed_files = []

    # Step 3: Process each file
    for uploaded in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        # Extract text and detect doc type
        text = extract_text(tmp_path)
        doc_type = detect_document_type(text)
        all_doc_types.append(doc_type)

        # Run AI compliance check
        issues = check_legal_issues(text, doc_type)

        # Prepare inline comments
        comments_map = {}
        for i, issue in enumerate(issues):
            comments_map[i] = f"{issue.get('issue')} | Suggestion: {issue.get('suggestion')}"

        # Save reviewed DOCX
        reviewed_path = tmp_path.replace(".docx", "_reviewed.docx")
        insert_comment(tmp_path, reviewed_path, comments_map)
        reviewed_files.append(reviewed_path)

        # Add to issue summary
        for issue in issues:
            summary["issues_found"].append({
                "document": doc_type,
                **issue
            })

    # Step 4: Compare against ADGM checklist
    required, missing = compare_with_checklist(process, all_doc_types)
    summary["required_documents"] = required
    summary["missing_documents"] = missing

    # Step 5: Show summary
    st.subheader("Review Summary")
    st.json(summary)

    # Step 6: Download reviewed files
    for file_path in reviewed_files:
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"Download Reviewed: {os.path.basename(file_path)}",
                data=f,
                file_name=os.path.basename(file_path)
            )

    # Step 7: Download summary JSON
    st.download_button(
        label="Download JSON Summary",
        data=json.dumps(summary, indent=2),
        file_name="summary.json"
    )

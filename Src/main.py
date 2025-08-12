from collections import defaultdict
from .document_reader import extract_text_from_docx
from .category_detector import detect_category
from .checklist import  compare_with_checklist
from .compliance_checker import run_compliance_check

def process_documents(uploaded_files):
    """
    Final pipeline:
    - Detect category per document
    - Group docs by category
    - For each category, compare with checklist & run compliance checks
    - Return aggregated JSON report per category
    """
    category_groups = defaultdict(list)

    # Step 1: Detect category for each doc
    for file in uploaded_files:
        text = extract_text_from_docx(file)
        category = detect_category(text)
        category_groups[category].append({
            "filename": file.name,
            "text": text
        })

    # Step 2: Build aggregated report per category
    final_report = []
    for category, docs in category_groups.items():
        uploaded_doc_names = [doc["filename"] for doc in docs]

        # Step 3: Checklist comparison
        checklist_data = compare_with_checklist(category, uploaded_doc_names)

        # Step 4: Compliance check (aggregate)
        all_issues = []
        for doc in docs:
            doc_issues = run_compliance_check([doc], category)
            all_issues.extend(doc_issues)

        category_report = {
            "process": category,
            "documents_uploaded": checklist_data["documents_uploaded"],
            "required_documents": checklist_data["required_documents"],
            "missing_document": checklist_data["missing_documents"] if checklist_data["missing_documents"] else None,
            "issues_found": all_issues
        }

        final_report.append(category_report)

    return final_report

import json
import os

with open("data/adgm_checklists.json", encoding="utf-8") as f:
    CHECKLISTS = json.load(f)

def get_required_docs_for_category(category):
    """
    Returns the list of required documents for a given category.
    If category not found, returns an empty list.
    """
    return CHECKLISTS.get(category, [])

def compare_with_checklist(category, uploaded_doc_names):
    """
    Compare uploaded document names with required checklist for a category.
    """
    required_docs = get_required_docs_for_category(category)
    
    # Normalize names (lowercase, remove extensions)
    uploaded_normalized = [
        os.path.splitext(doc)[0].strip().lower()
        for doc in uploaded_doc_names
    ]
    required_normalized = [doc.strip().lower() for doc in required_docs]

    # Find missing docs
    missing_docs = [
        req for req, req_norm in zip(required_docs, required_normalized)
        if req_norm not in uploaded_normalized
    ]

    return {
        "category": category,
        "documents_uploaded": len(uploaded_doc_names),
        "required_documents": len(required_docs),
        "missing_documents": missing_docs
    }

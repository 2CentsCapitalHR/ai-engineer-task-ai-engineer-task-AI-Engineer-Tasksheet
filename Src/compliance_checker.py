from .rag_engine import retrieve_context
from .llm import ask_llm
import json

def run_compliance_check(extracted_docs, category):
    """
    Runs Layer 2 compliance checks on all extracted documents.
    Uses RAG (retrieve_context) + Qwen LLM (ask_llm).
    Returns a list of issues per document.
    """
    issues = []

    for doc in extracted_docs:
        text = doc["text"]
        clauses = text.split("\n")  # basic split; can improve with clause detection

        for clause in clauses:
            if not clause.strip():
                continue

            # Step 1: Retrieve ADGM context for this clause
            context = retrieve_context(clause)

            # Step 2: Build LLM prompt
            prompt = f"""
You are an ADGM legal compliance assistant.
Given the clause below, check if it is compliant with ADGM rules.
If not, provide:
- issue: A short description of the problem
- severity: High / Medium / Low
- suggestion: A suggested fix
- citation: Exact ADGM law, rule, or template name that applies

Clause:
\"\"\"{clause}\"\"\"

Relevant ADGM Sources:
{context}

Return your answer in **valid JSON** format.
Example:
{{
    "issue": "...",
    "severity": "...",
    "suggestion": "...",
    "citation": "..."
}}
"""

            # Step 3: Ask Mistralai for compliance check
            try:
                response = ask_llm(prompt)

                # Step 4: Try parsing JSON output
                try:
                    parsed = json.loads(response)
                except json.JSONDecodeError:
                    parsed = {"raw_output": response}

                # Step 5: Append result
                issues.append({
                    "document": doc["filename"],
                    "clause": clause[:50] + ("..." if len(clause) > 50 else ""),
                    "result": parsed
                })

            except Exception as e:
                issues.append({
                    "document": doc["filename"],
                    "clause": clause[:50],
                    "error": str(e)
                })

    return issues

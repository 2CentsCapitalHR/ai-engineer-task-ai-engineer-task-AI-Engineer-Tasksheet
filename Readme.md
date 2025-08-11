# ADGM Corporate Agent — Document Intelligence Tool

A compliance-focused document review application for corporate agents operating under Abu Dhabi Global Market (ADGM) regulations. The `corporate_agent_app.py` script analyses corporate documents, verifies them against ADGM checklist requirements, flags regulatory risks, and produces annotated `.docx` reports with actionable recommendations.

---

## Overview

This application uses a combination of text extraction, rule-based checks, vector similarity search, and optional AI-powered clause generation to assess corporate documents such as **Articles of Association** and **Memorandum of Association**. It runs via an **interactive Gradio web interface** and can:

- Detect missing or incomplete mandatory documents.
- Identify incorrect jurisdiction references.
- Flag missing signatories.
- Highlight ambiguous or non-binding language.
- Detect placeholder or incomplete fields.

For deeper insight, it integrates **Retrieval-Augmented Generation (RAG)** using FAISS and Sentence Transformers, and optionally **Large Language Models (LLMs)** from OpenAI or Hugging Face to suggest compliant clauses.

---

## How the Code Works

1. **Imports and Environment Setup** — Loads required libraries (Gradio, python-docx, PyPDF2, FAISS, Sentence Transformers, dotenv, OpenAI/Hugging Face API clients) and environment variables.
2. **Document Extraction** — Reads `.docx` and `.pdf` files, extracting plain text for processing.
3. **Document Type Detection** — Matches keywords in the extracted text to predefined ADGM document categories.
4. **Checklist Matching** — Compares document content with regulatory checklists for incorporation, branch registration, and data protection.
5. **Red Flag Detection** — Applies keyword and regex-based patterns to detect non-compliance indicators such as wrong jurisdiction, missing signatories, or placeholders.
6. **Vector Index Search (RAG)** — Encodes reference documents into embeddings and retrieves contextually relevant text to support compliance checks.
7. **AI-Powered Suggestions** *(optional)* — Uses LLMs to draft or improve clauses based on detected issues.
8. **Annotation & Output** — Highlights problematic text in `.docx` files, adds inline comments, and generates an "Automated Review Summary".
9. **Web Interface** — A Gradio UI allows users to upload files, run analysis, and download reviewed outputs.

---

## Key Features

- Automated document classification via keyword mapping.
- Checklist compliance verification.
- Red flag detection for regulatory risks.
- Evidence retrieval using FAISS vector search.
- Optional LLM-based corrective clause generation.
- Annotated `.docx` outputs with highlights and summary.
- User-friendly Gradio dashboard.

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```


### 4. (Optional) Configure API Keys

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
HF_API_KEY=hf_...
```

---

## Running the Application

```bash
python corporate_agent_app.py
```

Access it via `http://127.0.0.1:7860`.

---

## Usage Guide

1. Upload corporate `.docx` files.
2. Upload ADGM reference documents.
3. (Optional) Enter API keys for AI suggestions.
4. Click **Run Review**.
5. Download annotated `.docx` outputs and review JSON summaries.

---

## Testing with Sample Files

- `Articles_of_Association.docx` — Contains non-ADGM jurisdiction and ambiguous wording.
- `Memorandum_of_Association.docx` — For checklist matching.

---




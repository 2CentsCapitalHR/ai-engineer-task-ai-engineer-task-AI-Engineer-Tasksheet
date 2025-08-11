# **ADGM Corporate Agent with Document Intelligence**

## **Overview**

The **ADGM Corporate Agent** is an AI-powered legal assistant designed to help review, validate, and prepare legal documents for business incorporation and compliance within the Abu Dhabi Global Market (ADGM) jurisdiction.

It accepts `.docx` files, automatically identifies document types, verifies completeness against ADGM checklists, detects legal red flags using a **Retrieval-Augmented Generation (RAG)** approach, and provides inline comments plus a downloadable marked-up version and a structured JSON report.

This solution is built to run **completely locally** on GPU-enabled machines using **open-source tools** — no paid APIs. It uses **FAISS** for vector similarity search, **Sentence Transformers** for embeddings, and **Ollama** for running a local Large Language Model (LLM) with GPU acceleration.

***

## **Key Features**

- Upload multiple legal `.docx` documents via a Streamlit web UI.
- Automatic **document type detection** (e.g., Articles of Association, Board Resolution).
- ADGM **checklist-based completeness verification**.
- Retrieval of **relevant ADGM law excerpts** from a local FAISS index built from official reference docs.
- **LLM-powered legal red flag detection** using Mistral (or other Ollama-supported models).
- Inline comment markers added to reviewed `.docx` files with compliance suggestions.
- **Downloadable** reviewed document and structured JSON report.
- Completely offline, local execution.

***

## **Technology Stack**

- **Python 3.10+**
- [Streamlit](https://streamlit.io/) — Fast UI for doc uploads and results.
- [python-docx](https://python-docx.readthedocs.io/) — Read and annotate Word `.docx`.
- [FAISS](https://github.com/facebookresearch/faiss) — Vector database for similarity search.
- [Sentence-Transformers](https://www.sbert.net/) — Embeddings generation (`all-MiniLM-L6-v2`).
- [PyPDF2](https://pypi.org/project/PyPDF2/) — PDF text extraction.
- [Ollama](https://ollama.com) — Run open-source LLMs locally with GPU (Metal on macOS).
- Local LLM Model — e.g., **`mistral`** or **`llama2`** pulled via Ollama.

***

## **Repository Structure**

```
.
├── adgm_faiss.index        # Generated FAISS index file
├── adgm_metadata.pkl       # Generated metadata for index
├── adgm_reference_docs     # Place your official PDFs/DOCXs here
├── app.py                  # Main Streamlit app
├── build_index.py          # Builds FAISS index from ADGM references
├── Readme.md               # This documentation
├── requirements.txt        # Dependencies list
```

***

## **Setup and Installation**

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/aeiou-sudo/Corporate-Agent.git
cd 
```

***

### 2️⃣ Create and Activate Virtual Environment

```bash
python3 -m venv corporate_agent_env
source corporate_agent_env/bin/activate   # macOS/Linux
# Windows:
# .\corporate_agent_env\Scripts\activate
```

***

### 3️⃣ Install Dependencies

With **requirements.txt**:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install streamlit python-docx sentence-transformers faiss-cpu pypdf PyPDF2 langchain ollama
```

***

### 4️⃣ Prepare ADGM Reference Documents and Build FAISS Index

1. Place all **official ADGM PDFs and DOCX references** inside:
   ```
   adgm_reference_docs/
   ```
2. Run:
   ```bash
   python build_index.py
   ```
   This will:
   - Extract text from `.pdf` & `.docx`
   - Chunk text for retrieval
   - Generate embeddings
   - Save:
     - `adgm_faiss.index`
     - `adgm_metadata.pkl`

> **You must run `build_index.py` before starting the app.**

***

### 5️⃣ Install and Start Ollama

#### Install Ollama (macOS or Linux):
```bash
brew install ollama
```

#### Start the Ollama service:
```bash
ollama serve
```

#### Pull a local LLM model:
```bash
ollama pull mistral
```
*(You may use `llama2` or another model, but update `model="..."` in `app.py` accordingly.)*

***

## **Running the Application**

After completing all setup:

```bash
streamlit run app.py
```

In your browser:
- Usually opens at **http://localhost:8501**
- Upload `.docx` files for review.

***

## **Using the Application**

1. **Upload `.docx` legal files** — relevant to your ADGM process.
2. App **detects** document types automatically.
3. App **checks** against ADGM mandatory document checklist.
4. Retrieves **related ADGM law excerpts** via FAISS RAG.
5. Sends to **local LLM** for analysis:
   - Lists compliance issues
   - Suggests clause improvements
   - Cites relevant laws
6. Adds **inline comment markers** to `.docx` output.
7. Displays **structured JSON report**.
8. Provides **download buttons** for:
   - Reviewed `.docx`
   - JSON report

***

## **Documents Supported**

- **Company Formation**:
  - Articles of Association (AoA)
  - Memorandum of Association (MoA)
  - Board Resolution
  - Incorporation Application Form
  - Register of Members and Directors
- Extendable for:
  - Licensing Filings
  - Employment/HR Contracts
  - Commercial Agreements
  - Compliance Policies

***

## **Notes & Limitations**

- Inline comments are **simulated** via bracketed italic text; true MS Word Review comments require advanced XML editing.
- Only runs locally using **Ollama** LLM — ensure `ollama serve` is active before starting the app.
- Ensure **model name** in `app.py` matches what you downloaded via `ollama pull`.
- Large reference sets and long documents may slow down processing — prefer smaller models for speed.

***

## **Example Folder Layout Before Running**

```
repo-root/
    ├── adgm_faiss.index
    ├── adgm_metadata.pkl
    ├── adgm_reference_docs
    │   ├── ADGM DPR 2021 Appropriate Policy Document.pdf
    │   ├── ADGM RA Name self declaration v2.docx
    │   ├── ADGM RA Service of Alcohol Guidance.pdf
    │   ├── ADGM RA Statement of Concurrence.docx
    │   ├── ADGM Standard Employment Contract - ER 2019 - Short Version (May 2024).docx
    │   ├── ADGM Standard Employment Contract Template - ER 2024 (Feb 2025).docx
    │   ├── ADGM Statutory Demand.docx
    │   ├── ADGM Supplementary Guidance on Whistleblowing July 2025.pdf
    │   ├── ADGM Unaudited Small Companies Regime Balance Sheet Template-unofficial.docx
    │   ├── adgm-onshore-government-authorities-approval-guidelines-003.docx
    │   ├── adgm-ra-model-articles-private-company-limited-by-guarantee.docx
    │   ├── adgm-ra-model-articles-private-company-limited-by-shares.docx
    │   ├── ADGM-RA-Nominee-Arrangement-Confirmation.docx
    │   ├── adgm-ra-resolution-corporate-shareholders-PLC-incorporation-v1.docx
    │   ├── adgm-ra-resolution-multiple-incorporate-shareholders-LTD-incorporation-v2.docx
    │   ├── adgm-ra-resolution-multiple-individual-shareholders-PLC-incorporation-v1.docx
    │   ├── adgm-ra-resolution-single-individual-shareholder-PLC-incorporation-v1.docx
    │   ├── ADGM-RA-Statement-of-Affairs.docx
    │   ├── Annual Accounts Extension Guidance V2.pdf
    │   ├── Articles-of-Association-Private-Company-Ltd-Guarantee.docx
    │   ├── Articles-of-Association-Private-Company-Ltd-Shares.docx
    │   ├── Beneficial Ownership and Control Guidance 2021.pdf
    │   ├── Branch - Financial Services and Non-Financial Services.pdf
    │   ├── Branch-Financial Services 20230509.pdf
    │   ├── Branch-Retail 20230509.pdf
    │   ├── Checklist Company Set Up V 1 20220530 Investment Company LTD ICC.pdf
    │   ├── Checklist Company Set Up V 1 20220530 Investment Company LTD PCC.pdf
    │   ├── Checklist Company Set Up V1020220517 PLC NonFinancial.pdf
    │   ├── Checklist Company SetUp V1 20220530 Investment Company LTD.pdf
    │   ├── Checklist Registration V1 20220509 non-exempt foundations.pdf
    │   ├── Checklist Registration V1 20220601 non-exempt Foundations Continuance.pdf
    │   ├── Checklist-SPV-Non-Exempt.pdf
    │   ├── Environmental Social and Governance Disclosures Guidance 2024.pdf
    │   ├── Guidance on client money - March 2023.pdf
    │   ├── Guidance on Exemptions from the requirement to appoint a CSP 08-04-2021.pdf
    │   ├── Guidance-on-Revising-Defective-Accounts-and-Reports.pdf
    │   ├── Incorporation-by-Body-Corporate.docx
    │   ├── Incorporation-by-Individual.docx
    │   ├── Limited Liability Partnership - Financial and Non-Financial firms.pdf
    │   ├── Limited Partnership - Financial and Non-Financial Services.pdf
    │   ├── Nominee-Arragement-Confirmation-Role-Holder-Nominee-Partnership.docx
    │   ├── Nominee-Arrangement-Confirmation-Role-Holder-Nominee-Company.docx
    │   ├── Nominee-Arrangement-Confirmation-Role-Holder-Nominee-Foundation.docx
    │   ├── NomineeArrangementConfirmationShareholderUBOV1120201006-002.docx
    │   ├── Private Company Limited by Guarantee Non-Financial Services 20231228.pdf
    │   ├── Private Company Limited by Shares - Non-Financial Services.pdf
    │   ├── Private Company Limited by Shares - Retail.pdf
    │   ├── Private Company Limited by Shares (RSC) - Non-Financial Services.pdf
    │   ├── Private Company Limited by Shares continuance fin non-fin retail ex spv 20231228.pdf
    │   ├── Private Company Limited by Shares continuance SPV 20231228.pdf
    │   ├── Private Company Limited by Shares-Financial Services 20230509.pdf
    │   ├── Private Company Limited by Shares-Non-Exempt-SPV 20230509.pdf
    │   ├── Quick Guide 1 Know-Your-Customer KYC 20230920.pdf
    │   ├── RA-Annual-Accounts-Guidance-V10-09092022.pdf
    │   ├── Register-of-Directors-template-v1.docx
    │   ├── Registration-of-Branch.docx
    │   ├── Resolution-Change-Registered-Address.docx
    │   ├── Template_RegisterofBeneficialOwners-v1-20220107.docx
    │   ├── Templates_SHReso_AmendmentArticles-v1-20220107.docx
    │   └── Voluntary Liquidation Guidance 2023.pdf
    ├── app.py
    ├── build_index.py
    ├── corporate_agent_env
    │   ├── bin
    │   ├── etc
    │   ├── include
    │   ├── lib
    │   ├── pyvenv.cfg
    │   └── share
    ├── misc
    │   ├── Data Sources.pdf
    │   ├── hello_streamlit.py
    │   ├── readme.txt
    │   └── Task.pdf
    ├── Readme.md
    ├── requirements.txt
    └── test_retrieval.py

9 directories, 72 files
```

***

## **Support**

If you face issues:
- Verify **virtual environment** and Python version.
- Confirm **Ollama** is running and the LLM model is installed.
- Ensure **FAISS index** and **metadata files** exist.
- Check Streamlit console logs for errors.

***

**Thank you for using ADGM Corporate Agent** — a modern example of integrating RAG, local AI inference, and document intelligence for legal compliance automation.

***
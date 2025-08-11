# ADGM Corporate Agent

An AI-powered legal document review and compliance checker specifically designed for Abu Dhabi Global Market (ADGM) legal processes.

## 🎯 Project Overview

The ADGM Corporate Agent is an intelligent document processing system that helps users prepare and validate legal documentation for business incorporation and compliance within the ADGM jurisdiction. The system uses RAG (Retrieval-Augmented Generation) technology with official ADGM sources to ensure legal accuracy and compliance.

## ✨ Key Features

- **📄 Document Type Identification**: Automatically identifies document types (AoA, MoA, Board Resolutions, etc.)
- **🔍 Red Flag Detection**: Detects compliance issues, jurisdiction errors, and missing clauses
- **📋 Process Recognition**: Identifies legal processes (Company Incorporation, Licensing, etc.)
- **✅ Completeness Checking**: Validates document sets against ADGM checklists
- **💬 Inline Comments**: Adds contextual comments with ADGM rule references
- **📊 Structured Reporting**: Generates comprehensive JSON analysis reports
- **🌐 RAG Integration**: Uses official ADGM sources for accurate legal guidance

## 🏛️ Supported Document Types

### Company Formation Documents
- Articles of Association (AoA)
- Memorandum of Association (MoA)
- Board Resolution Templates
- Shareholder Resolution Templates
- Incorporation Application Form
- UBO Declaration Form
- Register of Members and Directors
- Change of Registered Address Notice

### Other Categories
- Employment & HR Contracts
- Data Protection Policies
- Commercial Agreements
- Compliance & Risk Policies
- Licensing Applications

### 🎥 Demo Video
[Watch the Demo Video](https://drive.google.com/file/d/1QYioV__0BFXRb7ctAB0ASV78KUpPiuLh/view?usp=sharing)
### 📸 Screenshots

### Main Interface - Process Selection
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/a5456a7a-6e54-45a7-b364-f99d39327bab" />

---
### Document Upload Interface
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/0124b198-028a-41be-9a80-fbe2ab7a1bfa" />

---
### Analysis Results
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/afa2b768-48b9-44b3-a3f8-3993271e7812" />

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/9a41cc58-2aeb-45b6-9c53-f05aed19542a" />

---
### Red Flag Detection
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/9cbaea35-a8ff-4c0d-bab4-b6b3a8e46440" />

---
### Download Section
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/f24ab00c-5ab2-4962-a8d6-350843913862" />

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+ (recommended)
- OpenAI API key
- Windows/Linux/Mac environment

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd adgm-corporate-agent
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

-- Activate virtual environment --
Windows:
venv\Scripts\activate

Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt

```

### Step 4: Environment Configuration
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=False
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=docx,pdf
VECTOR_STORE_PATH=data/vector_store/
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVAL_TOP_K=5
LLM_MODEL=gpt-4
MAX_TOKENS=2048
TEMPERATURE=0.1
```

### Step 5: Initialize RAG System
```bash
Validate configuration
python config.py

Initialize RAG system with ADGM sources
python setup_rag.py
```

### Step 6: Run the Application
```bash
streamlit run app.py

```

The application will open in your browser at `http://localhost:8501`

---

## 📁 Project Structure
```
adgm-corporate-agent/
├── app.py                     # Main Streamlit app
├── requirements.txt           # Dependencies
├── config.py                  # Configuration settings
├── data/
│   ├── adgm_docs/             # Downloaded ADGM documents
│   └── vector_store/          # FAISS index
├── modules/
│   ├── __init__.py
│   ├── document_parser.py
│   ├── rag_system.py
│   ├── document_checker.py
│   ├── comment_inserter.py
│   └── report_generator.py
├── templates/
│   └── checklists.json        # Document requirements
└── examples/
    ├── input/                 # Sample documents
    └── output/                # Processed documents

```

## 🔧 Configuration

### ADGM Data Sources
The system uses official ADGM sources defined in `config.py`:
- Company formation guidance
- Employment contract templates
- Data protection policies
- Compliance requirements
- Official checklists

### Process Checklists
Document requirements are defined in `templates/checklists.json`:
- Company Incorporation: 5 required documents
- Licensing: 3 required documents
- Employment Setup: 3 required documents
- Branch Registration: 4 required documents

## 📊 Usage

### 1. Upload Documents
- Supported formats: `.docx`, `.pdf`
- Multiple file upload supported
- Maximum file size: 10MB per file

### 2. Document Analysis
- Automatic document type identification
- Process recognition based on document types
- Red flag detection and compliance checking
- Missing document identification

### 3. Review & Download
- Download reviewed documents with inline comments
- Download structured JSON analysis reports
- View detailed compliance metrics

## 🚨 Red Flag Detection

The system detects various compliance issues:

### High Severity
- ❌ Wrong jurisdiction (UAE Federal vs ADGM)
- ❌ Missing required clauses
- ❌ Invalid document structure

### Medium Severity
- ⚠️ Missing signature sections
- ⚠️ Incomplete information
- ⚠️ Non-standard formatting

### Low Severity
- ℹ️ Missing dates
- ℹ️ Minor formatting issues

## 📋 Example Output

### JSON Report Structure
```
{
"timestamp": "2025-01-10T10:30:00",
"analysis_summary": {
"process": "Company Incorporation",
"documents_uploaded": 5,
"required_documents": 5,
"completion_rate": 100.0,
"missing_documents": []
},
"issues_summary": {
"total_issues": 3,
"high_severity": 1,
"medium_severity": 2,
"low_severity": 0
},
"document_details": [
{
"filename": "articles_of_association.docx",
"document_type": "articles_of_association",
"issues_found": [
{
"type": "jurisdiction_error",
"severity": "high",
"message": "Document references non-ADGM jurisdiction",
"suggestion": "Update jurisdiction clause to specify ADGM Courts"
}
]
}
],
"recommendations": [
"Address high-severity issues before submission to ADGM"
]
}
```

## 🧪 Testing

### Sample Documents
Create test documents for different scenarios:

1. **Complete Set**: All 5 required documents for company incorporation
2. **Missing Documents**: Partial document set to test completion checking
3. **Red Flag Documents**: Documents with intentional compliance issues

### Test Document Types
- Articles of Association with correct ADGM jurisdiction
- Board Resolution with wrong jurisdiction (for red flag testing)
- Employment Contract with missing clauses
- UBO Declaration with proper format
- Register of Members with complete information

## 🔍 Troubleshooting

### Common Issues

#### Installation Problems
```bash
If numpy installation fails (Python 3.12+)
pip install "numpy>=1.26.0"

If sentence-transformers has Keras issues
pip install tf-keras

```

#### API Issues
```
Check OpenAI API key
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

Validate configuration
python config.py
```

#### File Upload Issues
- Ensure files are in `.docx` or `.pdf` format
- Check file size limits (10MB default)
- Verify documents contain extractable text (PDFs)

## 🏗️ Architecture

### RAG System
- **Embedding Model**: all-MiniLM-L6-v2
- **Vector Store**: FAISS
- **LLM**: OpenAI GPT-4
- **Data Sources**: Official ADGM websites and documents

### Document Processing Pipeline
1. **Upload** → File validation and temporary storage
2. **Parse** → Text extraction and content analysis
3. **Identify** → Document type and process recognition
4. **Check** → Compliance validation and red flag detection
5. **Comment** → Inline comment insertion
6. **Report** → JSON report generation
7. **Download** → Reviewed documents and reports

## 🛡️ Security & Compliance

- All processing is done locally
- No document content is sent to external services except OpenAI for embeddings
- Temporary files are automatically cleaned up
- Sensitive information is not logged


## 📄 License

This project is created for the ADGM Corporate Agent task evaluation.

## 📞 Support

For questions or issues:
- Check the troubleshooting section
- Review the configuration settings
- Ensure all dependencies are properly installed

## 🎯 Task Compliance

This project fulfills all requirements from the ADGM Corporate Agent task:

✅ **Functional Objectives**: Document parsing, type identification, red flag detection  
✅ **Document Checklist Verification**: Process recognition and completeness checking  
✅ **Technical Requirements**: Streamlit UI, RAG integration, structured outputs  
✅ **Document Types**: All specified categories supported  
✅ **Red Flag Detection**: Comprehensive compliance checking  
✅ **Inline Comments**: ADGM rule references and suggestions  
✅ **Output Format**: JSON reports and reviewed documents  

## 🏆 Key Achievements

- **Legal Accuracy**: Uses official ADGM sources for compliance checking
- **User-Friendly**: Intuitive web interface with clear feedback
- **Comprehensive**: Handles multiple document types and processes
- **Professional**: Production-ready code with proper error handling
- **Scalable**: Modular architecture for easy extension

---


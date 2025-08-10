[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/vgbm4cZ0)

---
## NOTE
I’m really grateful for this opportunity and excited to have made it to this stage. I’ve done my best to put this plan together with the information provided, and I’m more than happy to take on any feedback or suggestions to make it better. Working on this was a great learning experience, and I’d love the chance to join 2Cents Capital, keep learning, grow alongside the team, and contribute in a meaningful way.

---

# ADGM Corporate Agent

An AI-powered legal assistant for Abu Dhabi Global Market (ADGM) document compliance review and validation.

## 🚀 Features

- **Document Upload & Analysis**: Upload .docx documents for automated compliance checking
- **ADGM Compliance Validation**: Verify documents against ADGM regulations and requirements  
- **Red Flag Detection**: Identify legal issues, inconsistencies, and violations
- **Smart Document Markup**: Add contextual comments and highlights to original documents
- **Comprehensive Reporting**: Generate detailed JSON reports with findings and recommendations
- **RAG-Enhanced Analysis**: Retrieval-Augmented Generation using ADGM knowledge base
- **Gemini 2.0 Flash Integration**: Fast, efficient AI analysis with Google's latest model

## 📋 Supported Document Types

- **Memorandum of Association**
- **Articles of Association**
- **Company Registration Applications**
- **Board Resolutions**
- Additional corporate documents (extensible)

## 🛠️ Architecture

```
ADGM Corporate Agent
├── FastAPI Backend (Python)
│   ├── Document Processing & Analysis Pipeline
│   ├── Async Background Tasks
│   └── REST API Endpoints
├── Gemini 2.0 Flash API
│   ├── AI-Powered Analysis
│   └── Intelligent Document Review
├── ChromaDB Knowledge Base
│   ├── Vector Search
│   ├── Document Embeddings
│   └── Contextual Retrieval
└── Enhanced Validation Engine
    ├── ADGM Compliance Rules
    ├── Document Structure Analysis
    └── Smart Recommendations
```

## ⚡ Quick Start

### 1. Prerequisites

- Python 3.9+
- Google Gemini API key
- 2GB+ available disk space

### 2. Installation

```bash
# Clone repository
git clone <repository-url>
cd adgm-corporate-agent

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 3. Configuration

Edit `.env` file:

```bash
# Required: Get your API key from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Adjust settings
MAX_FILE_SIZE=52428800
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MAX_CONCURRENT_ANALYSES=5
```

### 4. Start the Server

```bash
# Using startup script (recommended)
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000`

## 📖 API Documentation

Once running, access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 API Endpoints

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload` | Upload document for analysis |
| `GET` | `/api/documents/{id}/status` | Check processing status |
| `GET` | `/api/documents/{id}/analyze` | Get analysis results |
| `GET` | `/api/documents/{id}/report` | Get detailed JSON report |
| `GET` | `/api/documents/{id}/download` | Download marked-up document |
| `DELETE` | `/api/documents/{id}` | Delete document and files |
| `GET` | `/api/documents` | List all processed documents |

### Validation & System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/adgm/validate` | Direct content validation |
| `GET` | `/api/system/status` | System status and statistics |

## 💻 CLI Client Usage

Test the API using the included CLI client:

```bash
# Document Analysis
python cli_client.py --file "memorandum.docx"              # Upload and analyze
python cli_client.py --status "document_id"                # Check status
python cli_client.py --analyze "document_id"               # Get results
python cli_client.py --report "document_id"                # Get detailed report
python cli_client.py --download "document_id" --output "reviewed_doc.docx"

# Knowledge Base Operations
python cli_client.py --kb-query "company name requirements"  # Query knowledge base
python cli_client.py --kb-stats                             # Show KB statistics
python cli_client.py --kb-refresh                           # Refresh knowledge base

# System Operations
python cli_client.py --system                               # Check system status
```

## 📊 Example Usage

### 1. Upload Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@memorandum.docx"
```

Response:
```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "data": {
    "document_id": "abc123-def456-789",
    "filename": "memorandum.docx",
    "status": "uploaded",
    "estimated_processing_time": "2-5 minutes"
  }
}
```

### 2. Check Status

```bash
curl "http://localhost:8000/api/documents/abc123-def456-789/status"
```

### 3. Get Analysis Results

```bash
curl "http://localhost:8000/api/documents/abc123-def456-789/analyze"
```

Response:
```json
{
  "success": true,
  "data": {
    "compliance_score": 85.5,
    "completeness_score": 92.0,
    "flags": [
      {
        "severity": "warning",
        "title": "Missing Director Information",
        "description": "Director residential address not specified",
        "suggested_fix": "Add complete director address as per ADGM requirements"
      }
    ],
    "missing_sections": ["Subscriber Details"],
    "summary": "Document mostly compliant with minor issues to address"
  }
}
```

## 🏗️ Project Structure

```
adgm-corporate-agent/
├── app/
│   ├── main.py                 # FastAPI application with async support
│   ├── models.py              # Comprehensive Pydantic models
│   ├── services/
│   │   ├── document_parser.py  # Document processing & structure analysis
│   │   ├── gemini_analyzer.py  # Gemini AI integration & rate limiting
│   │   ├── adgm_validator.py   # ADGM compliance validation engine
│   │   └── adgm_knowledge_extractor.py # Knowledge base & RAG system
│   └── utils/
│       ├── file_handler.py     # File operations & safety checks
│       └── report_generator.py # Report generation & formatting
├── data/
│   ├── chroma_db/             # Vector store & embeddings
│   └── adgm_knowledge/        # ADGM regulations & templates
├── scripts/
│   └── populate_knowledge.py  # Knowledge base setup
├── uploads/                   # Document upload directory
├── outputs/                   # Processed documents & reports
├── config.py                  # Enhanced configuration
├── requirements.txt           # Project dependencies
├── run.py                    # Advanced startup script
├── cli_client.py             # CLI testing & automation
└── README.md                 # Documentation
```

## 🔍 Key Components

### Models (models.py)
- Comprehensive Pydantic data models
- Strong type safety with validation
- Support for all document types and operations:
  - Document analysis and flags
  - Compliance checks and scoring
  - Knowledge base operations
  - API requests and responses
- Extensible enum types for categorization

### Document Parser
- Advanced text and structure extraction from .docx files
- Automatic document type classification using pattern matching
- Intelligent section recognition and validation
- Format-preserving markup with comment support
- File safety checks and size validation

### Gemini Analyzer
- Integration with Gemini 2.0 Flash for high-speed analysis
- Context-aware structured prompts with retry logic
- Smart rate limiting (10 requests/minute) and error handling
- Reliable JSON-mode responses with fallback options
- Async processing for better performance

### ADGM Validator
- Enhanced ChromaDB vector knowledge base integration
- RAG-powered document validation
- Multi-level validation pipeline
  - Structure validation against templates
  - Content compliance with ADGM rules
  - Cross-reference checking with knowledge base
- Smart recommendations with context
- Configurable scoring system

### Knowledge Base Management
- Automated knowledge extraction
- Support for multiple document sources:
  - Web scraping with rate limiting
  - PDF document processing
  - DOCX template analysis
- Efficient chunking and embedding
- Vector search capabilities

### Report Generator
- Executive summaries with priority highlights
- Detailed JSON reports with multiple sections
- Smart recommendations based on violations
- Multiple export formats with templating
- Document markup with inline suggestions

## ⚙️ Configuration Options

### Environment Variables

```bash
# API Configuration
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
MAX_TOKENS_PER_REQUEST=8000

# File Settings
MAX_FILE_SIZE=52428800        # 50MB max
ALLOWED_FILE_TYPES=[".docx"]  # Supported file types
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
DATA_DIR=data

# Processing Settings
MAX_CONCURRENT_ANALYSES=5

# Knowledge Base Settings
CHROMA_DB_PATH=data/chroma_db
ADGM_KNOWLEDGE_PATH=data/adgm_knowledge

# Web Scraping Configuration
WEB_SCRAPING_ENABLED=true
WEB_SCRAPING_TIMEOUT=30
RATE_LIMIT_DELAY=1

# Document Processing
PDF_PROCESSING_ENABLED=true
PDF_MAX_SIZE_MB=50
DOCX_MAX_SIZE_MB=20
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Document Type Configuration

Modify `config.py` to add new document types:

```python
ADGM_DOCUMENT_TYPES = {
    "new_doc_type": {
        "name": "New Document Type",
        "required_sections": ["section1", "section2"],
        "validation_rules": {...}
    }
}
```

## 🚨 Error Handling

The system includes comprehensive error handling:

- **File validation**: Size, format, and content checks
- **API rate limiting**: Prevents Gemini API throttling
- **Graceful degradation**: Fallback responses when AI analysis fails
- **Background processing**: Non-blocking document analysis
- **Resource cleanup**: Automatic file cleanup and memory management

## 📈 Performance

- **Gemini 2.0 Flash**: Sub-second AI analysis with rate limiting
- **Async processing**: Non-blocking operations with background tasks
- **Memory efficient**: Streams large documents with configurable chunk sizes
- **Rate limiting**: Smart API quotas (10 requests/minute)
- **Concurrent processing**: Up to 5 documents simultaneously
- **Vector Search**: Fast document retrieval with ChromaDB
- **Smart Caching**: Knowledge base with efficient embeddings

## 🔒 Security Considerations

- File type validation prevents malicious uploads
- Size limits prevent resource exhaustion
- API key protection through environment variables
- Input sanitization for all user content
- Temporary file cleanup

## 📚 ADGM Knowledge Base

The system includes a curated knowledge base of ADGM regulations:

- Company formation requirements
- Director and shareholder rules
- Share capital requirements
- Compliance obligations
- Prohibited activities

Add more regulations by placing documents in `data/adgm_knowledge/`

## 🧪 Testing

```bash
# Test with sample documents
python cli_client.py --file "test_documents/memorandum.docx"

# System health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/docs
```

## 🔄 Updates & Maintenance

### Adding New ADGM Regulations

1. Place regulation documents in `data/adgm_knowledge/`
2. Restart the service to re-index
3. Update validation rules in `config.py` if needed

### Monitoring

Check system status:
```bash
curl http://localhost:8000/api/system/status
```

Monitor logs for processing status and errors.

## 🚀 Deployment

### Production Deployment

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🆘 Support

For support and questions:

1. Check the [API documentation](http://localhost:8000/docs)
2. Review the logs for error details
3. Test with the CLI client for debugging
4. Verify Gemini API key configuration

## 🔮 Roadmap

- [ ] Web frontend interface
- [ ] Multi-language document support
- [ ] Advanced workflow automation
- [ ] Integration with ADGM systems
- [ ] Batch processing capabilities
- [ ] Enhanced document templates

---

**Ready to get started?** Follow the Quick Start guide above and begin analyzing ADGM documents with AI-powered compliance checking!

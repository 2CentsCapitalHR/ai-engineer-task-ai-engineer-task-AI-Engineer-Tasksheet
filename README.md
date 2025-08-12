# ADGM Corporate Agent - Document Intelligence System

An AI-powered legal assistant for reviewing, validating, and preparing documentation for business incorporation and compliance within the Abu Dhabi Global Market (ADGM) jurisdiction.

## 🎯 Features

- **Document Upload & Analysis**: Accept and parse .docx documents
- **Document Type Identification**: Automatically identify document types (AoA, MoA, Board Resolutions, etc.)
- **ADGM Compliance Checking**: Validate documents against ADGM rules and regulations
- **Red Flag Detection**: Identify legal inconsistencies and compliance issues
- **Document Checklist Verification**: Check for missing mandatory documents
- **Contextual Comments**: Insert comments directly into documents with ADGM law citations
- **RAG-Powered Analysis**: Use Retrieval-Augmented Generation with official ADGM documents
- **Structured Reporting**: Generate JSON reports with detailed findings
- **Process Recognition**: Automatically identify legal processes (incorporation, licensing, etc.)
- **Compliance Scoring**: Calculate compliance scores for documents and processes

## 🏗️ Project Structure

```
kaab/
├── src/
│   ├── core/           # Core processing logic
│   │   ├── document_parser.py      # Document parsing and type identification
│   │   ├── compliance_checker.py   # ADGM compliance checking
│   │   ├── checklist_verifier.py   # Document checklist verification
│   │   ├── document_annotator.py   # Document annotation with comments
│   │   └── processing_engine.py    # Main processing orchestrator
│   ├── rag/            # RAG implementation
│   │   ├── vector_store.py         # Vector database management
│   │   └── rag_system.py          # RAG-powered analysis
│   ├── ui/             # User interface
│   │   └── gradio_app.py          # Gradio web interface
│   ├── utils/          # Utility functions
│   │   ├── data_collector.py      # ADGM data collection
│   │   └── report_generator.py    # Report generation
│   ├── config.py       # Configuration settings
│   └── models.py       # Data models
├── data/
│   ├── vector_db/      # Vector database storage
│   ├── uploads/        # Uploaded documents
│   ├── outputs/        # Processed documents
│   └── adgm_docs/      # ADGM reference documents
├── demo/
│   ├── sample_documents/          # Sample documents for testing
│   └── create_sample_documents.py # Script to create samples
├── tests/              # Test files
│   ├── test_document_parser.py    # Parser tests
│   └── test_compliance_checker.py # Compliance tests
├── requirements.txt    # Python dependencies
├── main.py            # Application entry point
├── install.py         # Installation script
├── setup_rag.py       # RAG system setup
└── README.md          # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key or Anthropic API key
- Internet connection for downloading ADGM reference documents

### Automated Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kaab
```

2. Run the automated installer:
```bash
python install.py
```

3. Configure your API keys in `.env` file:
```bash
# Edit .env with your API keys
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

4. Run the application:
```bash
python main.py
```

5. Open your browser and navigate to `http://localhost:7860`

### Manual Installation

If you prefer manual setup:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Create directories:
```bash
mkdir -p data/{vector_db,uploads,outputs,adgm_docs}
mkdir -p demo/sample_documents
```

4. Setup RAG system:
```bash
python setup_rag.py --setup
```

5. Create sample documents:
```bash
python demo/create_sample_documents.py
```

6. Run the application:
```bash
python main.py
```

## 🔧 Configuration

Edit the `.env` file to configure:

- **API Keys**: OpenAI or Anthropic API keys
- **LLM Provider**: Choose between OpenAI or Anthropic
- **Model Selection**: Specify which model to use
- **File Processing**: Set file size limits and supported formats

## 📋 Supported Document Types

### Company Formation
- Articles of Association (AoA)
- Memorandum of Association (MoA)
- Incorporation Application Form
- UBO Declaration Form
- Board Resolution Templates
- Register of Members and Directors
- Shareholder Resolution Templates
- Change of Registered Address Notice

### Other Categories
- Employment Contracts
- Commercial Agreements
- Compliance Policies
- Licensing Documents

## 🎯 Usage

### Web Interface

1. **Upload Documents**:
   - Click "Upload DOCX Documents"
   - Select one or more .docx files
   - Supported formats: .docx only

2. **Analyze Documents**:
   - Click "🔍 Analyze Documents"
   - Wait for processing to complete
   - View progress in real-time

3. **Review Results**:
   - **Summary Tab**: Overview of findings and compliance score
   - **Detailed Report Tab**: Comprehensive analysis with specific issues
   - **JSON Report Tab**: Structured data for integration
   - **Download Tab**: Get marked-up documents with comments

4. **Download Outputs**:
   - Reviewed documents with highlighted issues and comments
   - JSON reports for further processing
   - HTML reports for sharing

### Sample Documents

Test the system with provided sample documents:

```bash
# Sample documents are in demo/sample_documents/
ls demo/sample_documents/
```

Sample documents include:
- **Articles of Association** (with jurisdiction issues)
- **Memorandum of Association** (missing sections)
- **Board Resolution** (missing dates)
- **Employment Contract** (generally compliant)

### Command Line Usage

You can also use components programmatically:

```python
from src.core.processing_engine import ADGMProcessingEngine
from src.rag.vector_store import initialize_vector_store

# Initialize system
vector_store = initialize_vector_store()
engine = ADGMProcessingEngine(vector_store)

# Process documents
result = engine.process_documents(['path/to/document.docx'])
print(result.analysis.overall_compliance_score)
```

## 🔍 Red Flag Detection

The system detects:
- Incorrect jurisdiction references
- Missing or invalid clauses
- Formatting issues
- Non-compliance with ADGM templates
- Ambiguous or non-binding language

## 📊 Output Format

### JSON Report Example
```json
{
  "process": "Company Incorporation",
  "documents_uploaded": 4,
  "required_documents": 5,
  "missing_document": "Register of Members and Directors",
  "issues_found": [
    {
      "document": "Articles of Association",
      "section": "Clause 3.1",
      "issue": "Jurisdiction clause does not specify ADGM",
      "severity": "High",
      "suggestion": "Update jurisdiction to ADGM Courts."
    }
  ]
}
```

## 🧪 Testing

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run specific test files:
```bash
pytest tests/test_document_parser.py
pytest tests/test_compliance_checker.py
```

Run tests with verbose output:
```bash
pytest tests/ -v
```

### Test Coverage

The test suite covers:
- Document parsing and type identification
- Compliance checking rules
- Red flag detection
- Document annotation
- RAG system functionality

### Manual Testing

1. **Test with Sample Documents**:
   ```bash
   python demo/create_sample_documents.py
   python main.py
   # Upload sample documents through web interface
   ```

2. **Test RAG System**:
   ```bash
   python setup_rag.py --test
   ```

3. **Test Individual Components**:
   ```bash
   python -c "from src.core.document_parser import DocumentParser; print('Parser OK')"
   python -c "from src.rag.vector_store import initialize_vector_store; print('Vector Store OK')"
   ```

## 📚 ADGM References

The system uses official ADGM documents and regulations from:
- [ADGM Registration Authority](https://www.adgm.com/registration-authority/registration-and-incorporation)
- [ADGM Setting Up](https://www.adgm.com/setting-up)
- [ADGM Legal Framework](https://www.adgm.com/legal-framework/guidance-and-policy-statements)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔧 Troubleshooting

### Common Issues

1. **"System not properly initialized"**:
   - Check that API keys are set in `.env` file
   - Verify internet connection for downloading ADGM documents
   - Run `python setup_rag.py --setup` to initialize RAG system

2. **"Failed to parse document"**:
   - Ensure file is in .docx format (not .doc)
   - Check that file is not corrupted
   - Verify file permissions

3. **"Processing failed"**:
   - Check API key validity and quota
   - Verify internet connection
   - Check logs for specific error messages

4. **"No documents could be parsed"**:
   - Ensure uploaded files are valid .docx documents
   - Check file size limits (default: 50MB)
   - Verify files are not password protected

### Performance Tips

- **Large Documents**: Break very large documents into smaller sections
- **Multiple Documents**: Process in batches for better performance
- **API Limits**: Monitor API usage to avoid rate limits
- **Memory Usage**: Restart application if processing many large documents

### Logs and Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check system status:
```bash
python -c "
from src.rag.vector_store import initialize_vector_store
vs = initialize_vector_store()
print(vs.get_collection_stats())
"
```

## 🔒 Security and Privacy

- **Data Processing**: Documents are processed locally
- **API Usage**: Only text content is sent to LLM APIs for analysis
- **Storage**: Uploaded documents are stored temporarily in `data/uploads/`
- **Cleanup**: Clear `data/uploads/` and `data/outputs/` regularly
- **API Keys**: Keep API keys secure and never commit them to version control

## 📈 Performance Metrics

The system provides several metrics:
- **Compliance Score**: 0-100% based on issues found
- **Processing Time**: Time taken for analysis
- **Document Coverage**: Percentage of required documents present
- **Issue Severity Distribution**: Breakdown of critical, high, medium, low issues

## 🆘 Support

### Getting Help

1. **Check Documentation**: Review this README and inline code comments
2. **Run Tests**: Use `pytest tests/` to verify system functionality
3. **Check Logs**: Enable debug logging for detailed error information
4. **Sample Documents**: Test with provided sample documents first

### Reporting Issues

When reporting issues, please include:
- Python version and operating system
- Error messages and stack traces
- Steps to reproduce the issue
- Sample documents (if not confidential)

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

## ⚠️ Important Disclaimers

**Legal Disclaimer**: This system is designed to assist with ADGM compliance but should not replace professional legal advice. Always consult with qualified legal professionals for important legal matters.

**AI Limitations**: While the system uses advanced AI models, it may not catch all issues or may flag false positives. Human review is essential.

**Data Accuracy**: The system is based on publicly available ADGM documents and regulations. Always verify against the latest official ADGM sources.

**No Warranty**: This software is provided "as is" without warranty of any kind. Use at your own risk.
# proj_kaab

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/vgbm4cZ0)



#  ADGM Document Compliance Checker

This project is a **two-layer compliance verification system** that automatically detects document categories, checks against ADGM checklists, and runs deeper compliance checks using RAG + LLM.

---
<img width="1917" height="958" alt="Screenshot 2025-08-11 161910" src="https://github.com/user-attachments/assets/b235bb5a-c083-4cec-8d89-1879a13a64a4" />

<img width="1915" height="961" alt="Screenshot 2025-08-11 161928" src="https://github.com/user-attachments/assets/8b39ffaf-6c64-4723-9342-0047c7080ed7" /> 

<img width="1917" height="957" alt="Screenshot 2025-08-11 161946" src="https://github.com/user-attachments/assets/e9d3ab65-57d7-43be-a365-e1ab677a8e83" />


##  Features
- **Layer 1** – Category detection & checklist verification  
  - Automatically classifies uploaded documents into one of 13 ADGM categories.  
  - Compares uploaded documents against the required checklist for that category.  

- **Layer 2** – RAG + LLM compliance check  
  - Uses FAISS vector store + Hugging Face embeddings.  
  - Qwen LLM is used for rule-based compliance analysis.  

- **Streamlit UI** for document upload & JSON report download.  
- **JSON report output** with detected category, missing docs, and compliance issues.

---

## Project Structure
```
.
├── build/                      # Vector store creation scripts
├── data/                       # Data Sources PDF & checklists
├── src/                        # Main processing modules
│   ├── main.py                  # Pipeline for processing documents
│   ├── document_reader.py       # DOCX/PDF text extraction
│   ├── category_detector.py     # Category detection logic
│   ├── checklist.py             # Checklist comparison
│   ├── compliance_checker.py    # LLM-based compliance verification
├── vectorstore/                 # FAISS index files
├── ui.py                        # Streamlit frontend
├── requirements.txt             # Python dependencies
└── README.md
```

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/2CentsCapitalHR/ai-engineer-task-geddadasaisuchendra.git
cd ai-engineer-task-geddadasaisuchendra
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate the environment  
**Windows (PowerShell)**:
```bash
venv\Scripts\activate
```
**Mac/Linux**:
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Add your API keys
- Create a `.env` file in the project root:
```env
HUGGINGFACEHUB_API_TOKEN=your_huggingface_key
```

### 6. Build the vector store
```bash
python build/build_vectorstore_from_pdf.py
```

### 7. Run the Streamlit app
```bash
streamlit run ui.py
```

---

##  Usage
1. Open the Streamlit web app.  
2. Upload one or more `.docx` or `.pdf` files.  
3. Click **Run Compliance Check**.  
4. View:
   - Detected category
   - Missing checklist documents
   - Compliance issues (Layer 2)  
5. Download the JSON compliance report.

---

##  Technologies Used
- **Python 3.11**
- **Streamlit** – UI
- **LangChain + Hugging Face** – Embeddings
- **FAISS** – Vector store
- **Qwen LLM** – Compliance reasoning

---

##  Limitations
- **Accuracy depends on LLM & embeddings** – Misclassification can occur if documents are ambiguous or incomplete.  
- **Checklist matching is name-based** – Document names must closely match the checklist items for detection.  
- **Limited document types** – Currently supports `.docx` and `.pdf` files only.  
- **Local vector store** – FAISS index must be rebuilt when the checklist data changes.  
- **Internet dependency** – Requires Hugging Face API for embeddings and Qwen for compliance reasoning.

---

##  Future Improvements
- **More robust category detection** using fine-tuned classification models.  
- **Fuzzy matching** for document names to handle variations.  
- **Support for additional file formats** such as `.xlsx`, `.txt`.  
- **Cloud-based vector store** for real-time updates without rebuilding.  
- **Integration with OCR** to handle scanned PDFs.  
- **Multi-category classification** if documents span multiple processes.

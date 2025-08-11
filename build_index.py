import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from PyPDF2 import PdfReader  # For PDFs
from docx import Document     # For DOCXs
import os

# -------- CONFIG --------
REFERENCE_DIR = "adgm_reference_docs"  # Name your folder as needed
supported_extensions = [".pdf", ".docx"]
reference_files = [
    os.path.join(REFERENCE_DIR, f)
    for f in os.listdir(REFERENCE_DIR)
    if os.path.splitext(f)[1].lower() in supported_extensions
]
INDEX_FILE = "adgm_faiss.index"
META_FILE = "adgm_metadata.pkl"

# -------- STEP 0: Helper functions --------

def read_pdf_text(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Could not read PDF {file_path}: {e}")
        return ""

def read_docx_text(file_path):
    try:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"Could not read DOCX {file_path}: {e}")
        return ""

# -------- STEP 1: Extract text from PDFs and Docx --------
documents = []
for file_path in reference_files:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        content = read_pdf_text(file_path)
        print(f"Parsed {file_path} (-PDF)")
    elif ext == ".docx":
        content = read_docx_text(file_path)
        print(f"Parsed {file_path} (-Docx)")
    else:
        content = ""
    if content.strip():
        documents.append({"source": os.path.basename(file_path), "content": content})
    else:
        print(f"Skipped {file_path} (could not extract text)")
# -------- STEP 2: Chunk text --------
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
docs = []
metadata = []
for ref in documents:
    chunks = splitter.split_text(ref["content"])
    for chunk in chunks:
        docs.append(chunk)
        metadata.append({"source": ref["source"], "length": len(chunk)})

# -------- STEP 3: Load embedding model --------
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")  # Efficient for CPU/M1

# -------- STEP 4: Create embeddings --------
print("Creating embeddings...")
embeddings = model.encode(docs, show_progress_bar=True)

# -------- STEP 5: Store in FAISS --------
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

faiss.write_index(index, INDEX_FILE)
with open(META_FILE, "wb") as f:
    pickle.dump({"metadata": metadata, "docs": docs}, f)

print(f"FAISS index built and stored as {INDEX_FILE}")


# build/master_build_vectorstore.py
import os
import re
import requests
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Config
VECTORSTORE_PATH = os.path.join("data", "vectorstore")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # one level up from /build
DATA_SOURCES_PDF = os.path.join(BASE_DIR, "data", "Data Sources.pdf")

# ------------- HELPERS -------------
def extract_links_from_pdf(pdf_path):
    """Extract category, document name, and link from Data Sources PDF."""
    reader = PdfReader(pdf_path)
    links_data = []
    current_category = None
    
    for page in reader.pages:
        text = page.extract_text()
        for line in text.split("\n"):
            url_match = re.search(r"(https?://\S+)", line)
            if not url_match:
                # If line is likely a category name
                if line.strip().isupper():
                    current_category = line.strip()
                continue
            url = url_match.group(1).strip()
            doc_name = line.replace(url, "").strip()
            links_data.append((current_category, doc_name, url))
    return links_data

def download_file(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return BytesIO(resp.content)

def parse_pdf(file_bytes):
    reader = PdfReader(file_bytes)
    return "\n".join([p.extract_text() or "" for p in reader.pages])

def parse_docx(file_bytes):
    doc = Document(file_bytes)
    return "\n".join([p.text for p in doc.paragraphs])

def parse_html(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.get_text(separator="\n")

# ------------- MAIN BUILD -------------
def build_vectorstore():
    links_data = extract_links_from_pdf(DATA_SOURCES_PDF)
    print(f"📄 Found {len(links_data)} documents in Data Sources PDF")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    all_texts = []
    all_metadata = []

    for category, doc_name, url in links_data:
        print(f"⬇️ Downloading: {doc_name} ({category})")
        try:
            if url.lower().endswith(".pdf"):
                text = parse_pdf(download_file(url))
            elif url.lower().endswith(".docx") or url.lower().endswith(".doc"):
                text = parse_docx(download_file(url))
            else:
                text = parse_html(url)

            chunks = splitter.split_text(text)
            all_texts.extend(chunks)
            all_metadata.extend([{
                "category": category,
                "source": doc_name,
                "url": url
            }] * len(chunks))
        except Exception as e:
            print(f"⚠️ Failed to process {url}: {e}")

    print("🛠 Building FAISS index...")
    vectorstore = FAISS.from_texts(all_texts, embedding=embeddings, metadatas=all_metadata)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"✅ Vectorstore saved at: {VECTORSTORE_PATH}")

if __name__ == "__main__":
    os.makedirs(VECTORSTORE_PATH, exist_ok=True)
    build_vectorstore()

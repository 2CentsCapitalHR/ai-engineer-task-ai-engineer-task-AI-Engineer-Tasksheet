import requests
import os
from bs4 import BeautifulSoup
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import json
from config import ADGM_URLS, ADGM_URL_CATEGORIES, get_all_urls
import time
from urllib.parse import urlparse

class ADGMRagSystem:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.texts = []
        self.metadata = []
        
        # Try to load existing vector store
        self.load_vector_store()
        
    def load_vector_store(self):
        """Load existing vector store if available"""
        try:
            if os.path.exists('data/vector_store/adgm_index.faiss'):
                self.index = faiss.read_index('data/vector_store/adgm_index.faiss')
                
                with open('data/vector_store/texts.pkl', 'rb') as f:
                    self.texts = pickle.load(f)
                    
                with open('data/vector_store/metadata.pkl', 'rb') as f:
                    self.metadata = pickle.load(f)
                    
                print(f"✅ Loaded existing vector store with {len(self.texts)} documents")
                return True
        except Exception as e:
            print(f"⚠️ Could not load existing vector store: {e}")
            
        return False
        
    def download_adgm_documents(self, category=None):
        """Download documents from ADGM URLs"""
        if category:
            urls = ADGM_URL_CATEGORIES.get(category, [])
        else:
            urls = get_all_urls()
        
        documents = []
        
        for url in urls:
            try:
                print(f"📥 Downloading: {url}")
                
                # Add delay to be respectful to servers
                time.sleep(1)
                
                # Set headers to mimic browser
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Handle different content types
                content_type = response.headers.get('content-type', '').lower()
                
                if 'text/html' in content_type:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    text = soup.get_text()
                    
                elif 'application/pdf' in content_type:
                    # For PDF files, you'd need to use PyPDF2 or similar
                    text = f"PDF document from {url}"
                    
                elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
                    # For DOCX files
                    text = f"DOCX template from {url}"
                    
                else:
                    # Try to get text anyway
                    text = response.text
                
                # Clean and validate text
                text = ' '.join(text.split())  # Clean whitespace
                
                if len(text.strip()) > 100:  # Only add substantial content
                    documents.append({
                        'url': url,
                        'content': text,
                        'source': 'ADGM Official',
                        'domain': urlparse(url).netloc,
                        'content_type': content_type
                    })
                    print(f"✅ Successfully processed: {url}")
                else:
                    print(f"⚠️ Skipping (insufficient content): {url}")
                    
            except Exception as e:
                print(f"❌ Error downloading {url}: {e}")
                continue
        
        print(f"\n📊 Successfully downloaded {len(documents)} documents")
        return documents
    
    def build_vector_store(self, documents):
        """Create FAISS vector store"""
        # Chunk documents
        chunks = []
        metadata = []
        
        for doc in documents:
            content = doc['content']
            # Split into chunks of 500 words
            words = content.split()
            for i in range(0, len(words), 500):
                chunk = ' '.join(words[i:i+500])
                chunks.append(chunk)
                metadata.append({
                    'source': doc['source'],
                    'url': doc['url'],
                    'chunk_id': i//500
                })
        
        # Generate embeddings
        embeddings = self.model.encode(chunks)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        self.texts = chunks
        self.metadata = metadata
        
        # Save index
        os.makedirs('data/vector_store', exist_ok=True)
        faiss.write_index(self.index, 'data/vector_store/adgm_index.faiss')
        with open('data/vector_store/texts.pkl', 'wb') as f:
            pickle.dump(self.texts, f)
        with open('data/vector_store/metadata.pkl', 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def search(self, query, k=5):
        """Search relevant documents - THIS WAS MISSING!"""
        if self.index is None or not self.texts:
            print("⚠️ Vector store not loaded. Returning empty results.")
            return []
            
        try:
            query_embedding = self.model.encode([query])
            distances, indices = self.index.search(query_embedding.astype('float32'), k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.texts):  # Ensure valid index
                    results.append({
                        'text': self.texts[idx],
                        'metadata': self.metadata[idx],
                        'score': distances[0][i]
                    })
            
            return results
        except Exception as e:
            print(f"Error in search: {e}")
            return []

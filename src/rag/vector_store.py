"""Vector store implementation for ADGM document retrieval."""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np
from ..config import settings

logger = logging.getLogger(__name__)


class ADGMVectorStore:
    """Vector store for ADGM documents and regulations."""
    
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or settings.vector_db_path
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="adgm_documents",
            metadata={"description": "ADGM legal documents and regulations"}
        )
        
        logger.info(f"Vector store initialized with {self.collection.count()} documents")
    
    def add_documents(self, documents: List[Dict[str, str]]) -> None:
        """Add documents to the vector store."""
        if not documents:
            return
        
        logger.info(f"Adding {len(documents)} documents to vector store...")
        
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        metadatas = []
        documents_text = []
        
        for i, doc in enumerate(documents):
            # Create unique ID
            doc_id = f"{doc.get('category', 'general')}_{i}_{hash(doc.get('content', ''))}"
            ids.append(doc_id)
            
            # Prepare text for embedding
            text_content = doc.get('content', '')
            if not text_content and 'file_path' in doc:
                # For documents, we'll need to extract text
                text_content = self._extract_text_from_file(doc['file_path'])
            
            documents_text.append(text_content)
            
            # Create metadata
            metadata = {
                'title': doc.get('title', ''),
                'source': doc.get('source', ''),
                'category': doc.get('category', 'general'),
                'type': doc.get('type', 'text')
            }
            if 'file_path' in doc:
                metadata['file_path'] = doc['file_path']
            
            metadatas.append(metadata)
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedding_model.encode(documents_text, show_progress_bar=True)
        
        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            documents=documents_text
        )
        
        logger.info(f"Successfully added {len(documents)} documents to vector store")
    
    def search(self, query: str, n_results: int = 5, category_filter: Optional[str] = None) -> List[Dict]:
        """Search for relevant documents."""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Prepare where clause for filtering
        where_clause = None
        if category_filter:
            where_clause = {"category": category_filter}
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where=where_clause
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
    
    def get_relevant_regulations(self, document_type: str, issue_type: str) -> List[Dict]:
        """Get relevant ADGM regulations for specific document types and issues."""
        query = f"{document_type} {issue_type} ADGM regulations requirements"
        return self.search(query, n_results=3, category_filter="legal_framework")
    
    def get_document_requirements(self, process_type: str) -> List[Dict]:
        """Get document requirements for a specific legal process."""
        query = f"{process_type} required documents checklist ADGM"
        return self.search(query, n_results=5, category_filter="compliance")
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file types."""
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                return self._extract_docx_text(file_path)
            elif file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Unsupported file type: {file_path.suffix}")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            return ""
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF files."""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            logger.warning("PyPDF2 not available for PDF extraction")
            return ""
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {e}")
            return ""
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX files."""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            logger.warning("python-docx not available for DOCX extraction")
            return ""
        except Exception as e:
            logger.error(f"Failed to extract DOCX text: {e}")
            return ""
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector store."""
        count = self.collection.count()
        
        # Get sample of metadata to analyze categories
        if count > 0:
            sample_results = self.collection.get(limit=min(count, 100))
            categories = {}
            types = {}
            
            for metadata in sample_results['metadatas']:
                category = metadata.get('category', 'unknown')
                doc_type = metadata.get('type', 'unknown')
                categories[category] = categories.get(category, 0) + 1
                types[doc_type] = types.get(doc_type, 0) + 1
        else:
            categories = {}
            types = {}
        
        return {
            'total_documents': count,
            'categories': categories,
            'types': types
        }


def initialize_vector_store() -> ADGMVectorStore:
    """Initialize and return the vector store."""
    return ADGMVectorStore()

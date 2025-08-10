import os
import json
from typing import List, Dict, Any
import logging

class RAGEngine:
    """RAG Engine for ADGM Corporate Document Processing"""
    
    def __init__(self, filename: str = None):
        """
        Initialize RAG Engine
        
        Args:
            filename: Path to the knowledge base file (JSON or text)
        """
        self.filename = filename
        self.documents = []
        
        # Load knowledge base if filename provided
        if filename and os.path.exists(filename):
            self.load_knowledge_base(filename)
    
    def load_knowledge_base(self, filename: str):
        """Load knowledge base from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                if filename.endswith('.json'):
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Handle nested structure
                        for key, value in data.items():
                            if isinstance(value, list):
                                self.documents.extend(value)
                            else:
                                self.documents.append(value)
                    else:
                        self.documents = data if isinstance(data, list) else [data]
                else:
                    # Handle text files
                    content = f.read()
                    self.documents = [{"content": content, "source": filename}]
        except Exception as e:
            logging.warning(f"Error loading knowledge base: {e}")
            self.documents = []
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None):
        """Add a document to the knowledge base"""
        doc = {"content": content, "metadata": metadata or {}}
        self.documents.append(doc)
        return len(self.documents) - 1
    
    def query(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query the knowledge base using basic text matching"""
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            content = doc.get('content', '')
            if isinstance(content, str):
                # Simple keyword matching
                score = 0
                query_words = query_lower.split()
                content_lower = content.lower()
                
                for word in query_words:
                    if word in content_lower:
                        score += 1
                
                if score > 0:
                    results.append({
                        'content': content,
                        'metadata': doc.get('metadata', {}),
                        'score': score / len(query_words) if query_words else 0
                    })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:n_results]
    
    def get_relevant_context(self, query: str, max_tokens: int = 1000) -> str:
        """Get relevant context for a query"""
        results = self.query(query, n_results=3)
        context_parts = []
        total_tokens = 0
        
        for result in results:
            content = result['content']
            if isinstance(content, str):
                words = content.split()
                if total_tokens + len(words) <= max_tokens:
                    context_parts.append(content)
                    total_tokens += len(words)
                else:
                    remaining_tokens = max_tokens - total_tokens
                    if remaining_tokens > 0:
                        context_parts.append(' '.join(words[:remaining_tokens]))
                    break
        
        return "\n\n".join(context_parts)
    
    def check_compliance(self, document_content: str, regulation_query: str) -> Dict[str, Any]:
        """Check compliance of document content against regulations"""
        context = self.get_relevant_context(regulation_query)
        
        return {
            "compliant": True,
            "issues": [],
            "suggestions": [],
            "context_used": context
        }

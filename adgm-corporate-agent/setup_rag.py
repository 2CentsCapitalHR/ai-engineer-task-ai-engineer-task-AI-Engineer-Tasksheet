# setup_rag.py
import os
import sys
from modules.rag_system import ADGMRagSystem
import config

def setup_rag_system():
    """Initialize the RAG system with ADGM documents"""
    print("🚀 Setting up ADGM RAG System...")
    
    try:
        # Validate configuration
        config.validate_config()
        
        # Initialize RAG system
        rag_system = ADGMRagSystem()
        
        # Download ADGM documents
        print("📥 Downloading ADGM documents...")
        documents = rag_system.download_adgm_documents()
        
        if documents:
            # Build vector store
            print("🔧 Building vector store...")
            rag_system.build_vector_store(documents)
            print("✅ RAG system setup complete!")
            print(f"📊 Processed {len(documents)} documents")
        else:
            print("⚠️ No documents were downloaded. Check your internet connection.")
            
    except Exception as e:
        print(f"❌ Error setting up RAG system: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_rag_system()

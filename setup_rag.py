"""Setup script to initialize the RAG system with ADGM data."""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.data_collector import collect_adgm_data
from src.rag.vector_store import initialize_vector_store

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_rag_system():
    """Setup the RAG system with ADGM data."""
    
    logger.info("🏛️ Setting up ADGM RAG System...")
    
    # Step 1: Collect ADGM data
    logger.info("📥 Collecting ADGM reference data...")
    try:
        adgm_data = collect_adgm_data()
        logger.info(f"✅ Collected {len(adgm_data)} items from ADGM sources")
    except Exception as e:
        logger.error(f"❌ Failed to collect ADGM data: {e}")
        return False
    
    # Step 2: Initialize vector store
    logger.info("🔍 Initializing vector store...")
    try:
        vector_store = initialize_vector_store()
        logger.info("✅ Vector store initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize vector store: {e}")
        return False
    
    # Step 3: Add documents to vector store
    logger.info("📚 Adding documents to vector store...")
    try:
        vector_store.add_documents(adgm_data)
        logger.info("✅ Documents added to vector store")
    except Exception as e:
        logger.error(f"❌ Failed to add documents to vector store: {e}")
        return False
    
    # Step 4: Verify setup
    logger.info("🔍 Verifying setup...")
    try:
        stats = vector_store.get_collection_stats()
        logger.info(f"✅ Vector store contains {stats['total_documents']} documents")
        logger.info(f"📊 Categories: {stats['categories']}")
        logger.info(f"📄 Types: {stats['types']}")
    except Exception as e:
        logger.error(f"❌ Failed to verify setup: {e}")
        return False
    
    logger.info("🎉 RAG system setup completed successfully!")
    return True


def test_rag_system():
    """Test the RAG system with sample queries."""
    
    logger.info("🧪 Testing RAG system...")
    
    try:
        vector_store = initialize_vector_store()
        
        # Test search functionality
        test_queries = [
            "Articles of Association requirements ADGM",
            "company incorporation documents checklist",
            "employment contract template ADGM",
            "jurisdiction clause requirements"
        ]
        
        for query in test_queries:
            logger.info(f"🔍 Testing query: {query}")
            results = vector_store.search(query, n_results=3)
            logger.info(f"✅ Found {len(results)} relevant documents")
            
            for i, result in enumerate(results[:2]):  # Show top 2 results
                title = result['metadata'].get('title', 'Unknown')
                category = result['metadata'].get('category', 'Unknown')
                logger.info(f"  {i+1}. {title} (Category: {category})")
        
        logger.info("🎉 RAG system test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG system test failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup ADGM RAG System")
    parser.add_argument("--test", action="store_true", help="Test the RAG system")
    parser.add_argument("--setup", action="store_true", help="Setup the RAG system")
    
    args = parser.parse_args()
    
    if args.setup or (not args.test and not args.setup):
        success = setup_rag_system()
        if not success:
            sys.exit(1)
    
    if args.test:
        success = test_rag_system()
        if not success:
            sys.exit(1)

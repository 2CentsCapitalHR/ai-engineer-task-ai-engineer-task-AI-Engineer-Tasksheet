#!/usr/bin/env python3
"""
One-time script to populate ADGM knowledge base
Run this once to set up your enhanced knowledge base
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.adgm_knowledge_extractor import ADGMKnowledgeExtractor

async def main():
    """Populate the ADGM knowledge base"""
    print("🚀 ADGM Knowledge Base Setup")
    print("=" * 40)
    
    # Initialize extractor
    extractor = ADGMKnowledgeExtractor()
    
    # Initialize and populate knowledge base
    print("📚 Initializing knowledge base...")
    success = await extractor.initialize_knowledge_base()
    
    if success:
        print("✅ Knowledge base populated successfully!")
        
        # Get stats
        stats = extractor.get_knowledge_stats()
        print(f"📊 Total documents: {stats.get('total_documents', 0)}")
        
        # Test query
        print("\n🔍 Testing knowledge base...")
        result = extractor.query_knowledge_base("company name requirements")
        print(f"✅ Test query found {result.get('count', 0)} results")
        
        print("\n🎉 ADGM Knowledge Base is ready!")
        print("You can now use the enhanced validator in your application.")
        
    else:
        print("❌ Failed to populate knowledge base")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)
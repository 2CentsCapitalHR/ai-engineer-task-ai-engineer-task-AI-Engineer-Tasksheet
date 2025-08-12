"""Installation and setup script for ADGM Corporate Agent."""

import subprocess
import sys
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"✅ Python version: {sys.version}")
    return True


def install_dependencies():
    """Install required dependencies."""
    logger.info("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    logger.info("📁 Creating directories...")
    
    directories = [
        "data",
        "data/vector_db",
        "data/uploads", 
        "data/outputs",
        "data/adgm_docs",
        "demo/sample_documents"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created: {directory}")
    
    logger.info("✅ Directories created")


def setup_environment():
    """Set up environment configuration."""
    logger.info("⚙️ Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        logger.info("✅ Created .env file from .env.example")
        logger.warning("⚠️ Please edit .env file with your API keys")
    else:
        logger.info("✅ Environment file already exists")


def create_sample_documents():
    """Create sample documents for testing."""
    logger.info("📄 Creating sample documents...")
    
    try:
        # Import and run the sample document creator
        sys.path.append(str(Path(__file__).parent))
        from demo.create_sample_documents import create_sample_documents
        create_sample_documents()
        logger.info("✅ Sample documents created")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create sample documents: {e}")
        return False


def setup_rag_system():
    """Set up the RAG system with ADGM data."""
    logger.info("🔍 Setting up RAG system...")
    
    try:
        # Run the RAG setup script
        subprocess.check_call([sys.executable, "setup_rag.py", "--setup"])
        logger.info("✅ RAG system setup completed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to setup RAG system: {e}")
        logger.info("💡 You can run 'python setup_rag.py --setup' manually later")
        return False


def test_installation():
    """Test the installation."""
    logger.info("🧪 Testing installation...")
    
    try:
        # Test imports
        sys.path.append(str(Path(__file__).parent / "src"))
        
        from src.core.document_parser import DocumentParser
        from src.core.compliance_checker import ADGMComplianceChecker
        from src.rag.vector_store import initialize_vector_store
        
        # Test basic functionality
        parser = DocumentParser()
        checker = ADGMComplianceChecker()
        
        logger.info("✅ Core components imported successfully")
        
        # Test vector store
        try:
            vector_store = initialize_vector_store()
            stats = vector_store.get_collection_stats()
            logger.info(f"✅ Vector store initialized with {stats['total_documents']} documents")
        except Exception as e:
            logger.warning(f"⚠️ Vector store test failed: {e}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Installation test failed: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    logger.info("\n🎉 Installation completed!")
    
    print("\n" + "="*60)
    print("🏛️ ADGM CORPORATE AGENT - INSTALLATION COMPLETE")
    print("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("\n1. Configure API Keys:")
    print("   - Edit the .env file with your OpenAI or Anthropic API key")
    print("   - Choose your preferred LLM provider")
    
    print("\n2. Run the Application:")
    print("   python main.py")
    
    print("\n3. Access the Interface:")
    print("   Open your browser to: http://localhost:7860")
    
    print("\n4. Test with Sample Documents:")
    print("   - Sample documents are available in demo/sample_documents/")
    print("   - Upload them through the web interface to test the system")
    
    print("\n5. Optional - Run Tests:")
    print("   pytest tests/")
    
    print("\n📚 DOCUMENTATION:")
    print("   - README.md: Complete setup and usage guide")
    print("   - demo/: Sample documents and examples")
    print("   - tests/: Test files for validation")
    
    print("\n⚠️ IMPORTANT:")
    print("   - This tool assists with ADGM compliance")
    print("   - Always consult qualified legal professionals")
    print("   - Review all AI-generated suggestions carefully")
    
    print("\n💡 SUPPORT:")
    print("   - Check logs for any issues")
    print("   - Ensure all dependencies are properly installed")
    print("   - Verify API keys are correctly configured")
    
    print("\n" + "="*60)


def main():
    """Main installation function."""
    logger.info("🏛️ Starting ADGM Corporate Agent Installation...")
    
    success = True
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not install_dependencies():
        success = False
    
    # Step 3: Create directories
    create_directories()
    
    # Step 4: Setup environment
    setup_environment()
    
    # Step 5: Create sample documents
    if not create_sample_documents():
        success = False
    
    # Step 6: Setup RAG system (optional, can fail)
    setup_rag_system()
    
    # Step 7: Test installation
    if not test_installation():
        success = False
    
    # Step 8: Print next steps
    print_next_steps()
    
    if not success:
        logger.warning("⚠️ Installation completed with some warnings")
        logger.info("💡 Check the logs above and resolve any issues")
    else:
        logger.info("✅ Installation completed successfully!")
    
    return success


if __name__ == "__main__":
    main()

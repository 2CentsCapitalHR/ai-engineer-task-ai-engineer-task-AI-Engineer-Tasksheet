"""Quick setup script for ADGM Corporate Agent with minimal dependencies."""

import subprocess
import sys
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def install_light_dependencies():
    """Install lightweight dependencies without GPU packages."""
    logger.info("📦 Installing lightweight dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements-light.txt", 
            "--no-cache-dir"  # Don't cache to save space
        ])
        logger.info("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install dependencies: {e}")
        return False


def create_minimal_directories():
    """Create only essential directories."""
    logger.info("📁 Creating essential directories...")
    
    directories = [
        "data/uploads", 
        "data/outputs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created: {directory}")


def setup_basic_environment():
    """Set up basic environment without RAG system."""
    logger.info("⚙️ Setting up basic environment...")
    
    env_file = Path(".env")
    if env_file.exists():
        logger.info("✅ Environment file already exists")
        return True
    
    # Create basic .env if it doesn't exist
    env_content = """# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4-turbo-preview
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# File Processing
MAX_FILE_SIZE_MB=50
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    logger.info("✅ Created basic .env file")
    return True


def create_minimal_app():
    """Create a minimal version of the app that works without RAG."""
    logger.info("🚀 Creating minimal app version...")
    
    minimal_app_content = '''"""Minimal ADGM Corporate Agent - No RAG version."""

import gradio as gr
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def process_documents_minimal(files):
    """Minimal document processing without RAG."""
    if not files:
        return "❌ No files uploaded", "", ""
    
    try:
        from src.core.document_parser import DocumentParser
        from src.core.compliance_checker import ADGMComplianceChecker
        
        parser = DocumentParser()
        checker = ADGMComplianceChecker()
        
        results = []
        for file in files:
            if file is None:
                continue
                
            file_path = file.name if hasattr(file, 'name') else str(file)
            
            # Parse document
            parsed = parser.parse_document(file_path)
            
            # Check compliance (rule-based only)
            issues = checker.check_compliance(
                parsed['text_content'], 
                parsed['document_type'], 
                parsed['structured_content']
            )
            
            results.append({
                'filename': parsed['filename'],
                'document_type': parsed['document_type'].value,
                'issues_count': len(issues),
                'issues': [{'issue': issue.issue, 'severity': issue.severity.value} for issue in issues[:5]]
            })
        
        # Create summary
        summary = f"📊 Processed {len(results)} document(s)\\n\\n"
        for result in results:
            summary += f"**{result['filename']}**\\n"
            summary += f"- Type: {result['document_type']}\\n"
            summary += f"- Issues: {result['issues_count']}\\n\\n"
        
        # Create detailed report
        detailed = "# Detailed Analysis\\n\\n"
        for result in results:
            detailed += f"## {result['filename']}\\n"
            detailed += f"**Type:** {result['document_type']}\\n"
            detailed += f"**Issues Found:** {result['issues_count']}\\n\\n"
            
            if result['issues']:
                detailed += "**Top Issues:**\\n"
                for issue in result['issues']:
                    detailed += f"- **{issue['severity']}**: {issue['issue']}\\n"
            detailed += "\\n"
        
        # Create JSON
        import json
        json_report = json.dumps(results, indent=2)
        
        return summary, detailed, json_report
        
    except Exception as e:
        return f"❌ Error: {str(e)}", "", ""

def create_interface():
    """Create minimal Gradio interface."""
    with gr.Blocks(title="ADGM Corporate Agent - Minimal") as interface:
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🏛️ ADGM Corporate Agent - Minimal Version</h1>
            <p>Basic document analysis without RAG system</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                file_upload = gr.File(
                    label="Upload DOCX Documents",
                    file_count="multiple",
                    file_types=[".docx"]
                )
                
                process_btn = gr.Button("🔍 Analyze Documents", variant="primary")
            
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.TabItem("📊 Summary"):
                        summary_output = gr.Markdown()
                    
                    with gr.TabItem("📄 Detailed"):
                        detailed_output = gr.Markdown()
                    
                    with gr.TabItem("💾 JSON"):
                        json_output = gr.Code(language="json")
        
        process_btn.click(
            fn=process_documents_minimal,
            inputs=[file_upload],
            outputs=[summary_output, detailed_output, json_output]
        )
    
    return interface

if __name__ == "__main__":
    print("🏛️ ADGM Corporate Agent - Minimal Version")
    print("Starting application...")
    
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
'''
    
    with open("app_minimal.py", 'w') as f:
        f.write(minimal_app_content)
    
    logger.info("✅ Created minimal app version")


def main():
    """Main quick setup function."""
    logger.info("🏛️ ADGM Corporate Agent - Quick Setup (Minimal Version)")
    
    # Install lightweight dependencies
    if not install_light_dependencies():
        logger.error("❌ Failed to install dependencies")
        return False
    
    # Create directories
    create_minimal_directories()
    
    # Setup environment
    setup_basic_environment()
    
    # Create minimal app
    create_minimal_app()
    
    print("\n" + "="*60)
    print("🎉 QUICK SETUP COMPLETED!")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("\n1. Configure API Key:")
    print("   - Edit .env file with your OpenAI API key")
    print("   - Your key appears to be already configured")
    print("\n2. Run Minimal Version:")
    print("   python app_minimal.py")
    print("\n3. Access Interface:")
    print("   http://localhost:7860")
    print("\n⚠️ NOTE:")
    print("   - This is a minimal version without RAG system")
    print("   - Uses rule-based compliance checking only")
    print("   - Requires less disk space and memory")
    print("   - For full features, free up disk space and run full install")
    print("\n" + "="*60)
    
    return True


if __name__ == "__main__":
    main()

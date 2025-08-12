"""Main entry point for ADGM Corporate Agent."""

import gradio as gr
import os
from pathlib import Path

# Create necessary directories
Path("data").mkdir(exist_ok=True)
Path("data/vector_db").mkdir(exist_ok=True)
Path("data/uploads").mkdir(exist_ok=True)
Path("data/outputs").mkdir(exist_ok=True)
Path("data/adgm_docs").mkdir(exist_ok=True)

def main():
    """Main function to launch the application."""
    print("🏛️ ADGM Corporate Agent - Document Intelligence System")
    print("=" * 60)
    
    # Import here to avoid circular imports
    from src.ui.gradio_app import create_gradio_interface
    
    # Create and launch the Gradio interface
    app = create_gradio_interface()
    
    # Launch the app
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

if __name__ == "__main__":
    main()

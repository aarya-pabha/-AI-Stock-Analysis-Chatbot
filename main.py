import sys
import logging
from src.ui.app import create_ui

# Set up logging for the terminal to track agent execution
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    """Main entry point to launch the Gradio Chatbot interface."""
    print("Initializing AI Stock Analysis Chatbot...")
    
    app = create_ui()
    
    # Launch the Gradio app on the default port (7860) for HF Spaces / Docker
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)

if __name__ == "__main__":
    main()

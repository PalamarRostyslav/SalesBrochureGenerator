"""UI launcher for the Sales Brochure Generator"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from .gradio_interface import GradioInterface
from ..configs.settings import validate_config
from ..utils.logger import get_logger

logger = get_logger("ui_launcher")

def launch_ui(share: bool = False, debug: bool = False, port: int = 7860):
    """Launch the Gradio UI interface"""
    try:
        # Validate basic configuration
        validate_config()
        
        # Create and launch interface
        ui = GradioInterface()
        logger.success("Starting Gradio interface...")
        ui.launch(share=share, debug=debug, server_port=port)
        
    except KeyboardInterrupt:
        logger.warning("UI launcher interrupted by user")
    except Exception as e:
        logger.error("Failed to launch UI", e)
        raise

if __name__ == "__main__":
    launch_ui()
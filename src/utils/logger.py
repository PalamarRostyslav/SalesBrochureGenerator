"""Enhanced logging utilities for the Sales Brochure Generator."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config.settings import LOGS_DIR, LOG_LEVEL

class EnhancedLogger:
    """Enhanced logger with rich formatting and progress tracking"""
    
    def __init__(self, name: str = "brochure_generator"):
        self.name = name
        self.console = Console()
        self.logger = self._setup_logger()
        self._current_progress: Optional[Progress] = None
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logger with file and console handlers"""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        if logger.handlers:
            return logger
        
        log_file = LOGS_DIR / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        rich_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True
        )
        rich_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(rich_handler)
        
        return logger
    
    def info(self, message: str, extra_data: dict = None):
        """Log info message with optional extra data"""
        if extra_data:
            message = f"{message} | {extra_data}"
        self.logger.info(message)
    
    def error(self, message: str, exception: Exception = None):
        """Log error message with optional exception"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def success(self, message: str):
        """Log success message with green color"""
        self.console.print(f"✅ {message}", style="green")
        self.logger.info(f"SUCCESS: {message}")
    
    def step(self, message: str):
        """Log a process step with blue color"""
        self.console.print(f"🔄 {message}", style="blue")
        self.logger.info(f"STEP: {message}")
    
    def safe_print(self, text: str):
        """Safely print text with Unicode error handling"""
        try:
            self.console.print(text)
        except UnicodeEncodeError:
            safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
            self.console.print(safe_text)
    
    def start_progress(self, description: str) -> Progress:
        """Start a progress spinner"""
        self._current_progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
        self._current_progress.start()
        self._current_progress.add_task(description=description)
        return self._current_progress
    
    def stop_progress(self):
        """Stop the current progress spinner"""
        if self._current_progress:
            self._current_progress.stop()
            self._current_progress = None
    
    def print_header(self, title: str):
        """Print a formatted header"""
        self.console.print()
        self.console.print(f"{'='*60}", style="cyan")
        self.console.print(f"{title:^60}", style="cyan bold")
        self.console.print(f"{'='*60}", style="cyan")
        self.console.print()
    
    def print_separator(self):
        """Print a separator line"""
        self.console.print("-" * 60, style="dim")

# Global logger instance
logger = EnhancedLogger()

def get_logger(name: str = None) -> EnhancedLogger:
    """Get a logger instance"""
    if name:
        return EnhancedLogger(name)
    return logger
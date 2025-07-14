"""File handling utilities for the Sales Brochure Generator"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from ..configs.settings import OUTPUT_DIR
from .text_utils import sanitize_filename
from .logger import get_logger

logger = get_logger(__name__)

class FileHandler:
    """Handle file operations for brochure generation"""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_brochure(self, content: str, company_name: str, language: str = 'en', format_type: str = 'md') -> Path:
        """Save brochure content to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_company_name = sanitize_filename(company_name)
        
        if language != 'en':
            filename = f"{safe_company_name}_brochure_{language}_{timestamp}.{format_type}"
        else:
            filename = f"{safe_company_name}_brochure_{timestamp}.{format_type}"
        
        file_path = self.output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.success(f"Brochure saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save brochure", e)
            raise
    
    def save_metadata(self, metadata: Dict[str, Any], company_name: str) -> Path:
        """Save generation metadata to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_company_name = sanitize_filename(company_name)
        filename = f"{safe_company_name}_metadata_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Metadata saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save metadata", e)
            raise
    
    def load_brochure(self, file_path: Path) -> Optional[str]:
        """Load brochure content from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load brochure from {file_path}", e)
            return None
    
    def list_brochures(self, company_name: str = None) -> list:
        """List all generated brochures"""
        pattern = "*.md"
        if company_name:
            safe_company_name = sanitize_filename(company_name)
            pattern = f"{safe_company_name}_brochure_*.md"
        
        try:
            files = list(self.output_dir.glob(pattern))
            return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
        except Exception as e:
            logger.error(f"Failed to list brochures", e)
            return []
    
    def delete_brochure(self, file_path: Path) -> bool:
        """Delete a brochure file"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted brochure: {file_path}")
                return True
            else:
                logger.warning(f"Brochure file not found: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete brochure", e)
            return False
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information and metadata"""
        try:
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_birthtime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'path': str(file_path)
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}", e)
            return {}
    
    def cleanup_files(self, days_old: int = None) -> int:
        """Clean up files from output directory"""
        from datetime import timedelta
        
        cutoff_date = None
        deleted_count = 0
        
        if days_old is not None:
            cutoff_date = datetime.now() - timedelta(days=days_old)
        
        try:
            for file_path in self.output_dir.glob("*"):
                if not file_path.is_file():
                    continue
                
                should_delete = True
                
                if cutoff_date is not None:
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    should_delete = file_time < cutoff_date
                    
                if should_delete:
                    file_path.unlink()
                    deleted_count += 1 
            
            action = f"older than {days_old} days" if days_old else "all"
            logger.info(f"Cleaned up {deleted_count} {action} files")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old files", e)
            return 0

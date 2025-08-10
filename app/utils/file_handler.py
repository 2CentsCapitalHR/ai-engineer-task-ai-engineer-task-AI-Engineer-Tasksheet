import os
import shutil
import aiofiles
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4
from datetime import datetime

from config import settings

class FileHandler:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)
        
        # Ensure directories exist
        self.upload_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return file path"""
        try:
            # Generate unique filename
            file_ext = Path(filename).suffix
            unique_filename = f"{uuid4()}{file_ext}"
            file_path = self.upload_dir / unique_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            return str(file_path)
            
        except Exception as e:
            raise Exception(f"Failed to save uploaded file: {str(e)}")
    
    def validate_file(self, filename: str, file_size: int) -> Dict[str, bool]:
        """Validate uploaded file"""
        validation = {
            'valid_extension': False,
            'valid_size': False,
            'valid_filename': False
        }
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        validation['valid_extension'] = file_ext in settings.ALLOWED_FILE_TYPES
        
        # Check file size
        validation['valid_size'] = file_size <= settings.MAX_FILE_SIZE
        
        # Check filename (no special characters)
        validation['valid_filename'] = filename.isascii() and len(filename) < 255
        
        return validation
    
    def generate_document_id(self) -> str:
        """Generate unique document ID"""
        return str(uuid4())
    
    def get_file_info(self, file_path: str) -> Dict:
        """Get file information"""
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        stat = path.stat()
        
        return {
            'filename': path.name,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': path.suffix.lower()
        }
    
    async def create_output_file(self, document_id: str, filename: str, content: bytes = None) -> str:
        """Create output file for processed document"""
        try:
            # Create output filename
            base_name = Path(filename).stem
            ext = Path(filename).suffix
            output_filename = f"{document_id}_{base_name}_reviewed{ext}"
            output_path = self.output_dir / output_filename
            
            if content:
                async with aiofiles.open(output_path, 'wb') as f:
                    await f.write(content)
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Failed to create output file: {str(e)}")
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return Path(file_path).exists()
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        try:
            Path(file_path).unlink(missing_ok=True)
            return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def cleanup_old_files(self, days_old: int = 7):
        """Clean up files older than specified days"""
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
        
        for directory in [self.upload_dir, self.output_dir]:
            for file_path in directory.glob("*"):
                if file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        print(f"Deleted old file: {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {str(e)}")
    
    def get_available_space(self) -> Dict[str, int]:
        """Get available disk space"""
        try:
            statvfs = os.statvfs(self.upload_dir)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            total_space = statvfs.f_frsize * statvfs.f_blocks
            
            return {
                'free_space_mb': free_space // (1024 * 1024),
                'total_space_mb': total_space // (1024 * 1024)
            }
        except Exception:
            return {'free_space_mb': 0, 'total_space_mb': 0}
    
    async def copy_file(self, source_path: str, destination_path: str) -> bool:
        """Copy file from source to destination"""
        try:
            async with aiofiles.open(source_path, 'rb') as src:
                content = await src.read()
                
            async with aiofiles.open(destination_path, 'wb') as dst:
                await dst.write(content)
                
            return True
        except Exception as e:
            print(f"Error copying file: {str(e)}")
            return False
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """Create backup of file"""
        try:
            source = Path(file_path)
            if not source.exists():
                return None
            
            backup_name = f"{source.stem}_backup_{int(datetime.now().timestamp())}{source.suffix}"
            backup_path = source.parent / backup_name
            
            shutil.copy2(source, backup_path)
            return str(backup_path)
            
        except Exception as e:
            print(f"Error creating backup: {str(e)}")
            return None
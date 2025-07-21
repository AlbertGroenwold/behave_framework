import os
import shutil
import zipfile
import logging
from pathlib import Path
from typing import List
import datetime
import hashlib
import tempfile


class FileUtils:
    """Utility class for file operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_directory(self, directory_path: str) -> bool:
        """
        Create directory if it doesn't exist
        
        Args:
            directory_path (str): Path to directory
        
        Returns:
            bool: True if successful
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Directory created/exists: {directory_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating directory {directory_path}: {e}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file
        
        Args:
            file_path (str): Path to file
        
        Returns:
            bool: True if successful
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"File deleted: {file_path}")
                return True
            else:
                self.logger.warning(f"File not found: {file_path}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def delete_directory(self, directory_path: str) -> bool:
        """
        Delete a directory and all its contents
        
        Args:
            directory_path (str): Path to directory
        
        Returns:
            bool: True if successful
        """
        try:
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)
                self.logger.info(f"Directory deleted: {directory_path}")
                return True
            else:
                self.logger.warning(f"Directory not found: {directory_path}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error deleting directory {directory_path}: {e}")
            return False
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copy a file
        
        Args:
            source_path (str): Source file path
            destination_path (str): Destination file path
        
        Returns:
            bool: True if successful
        """
        try:
            # Create destination directory if it doesn't exist
            Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_path, destination_path)
            self.logger.info(f"File copied from {source_path} to {destination_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error copying file from {source_path} to {destination_path}: {e}")
            return False
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Move a file
        
        Args:
            source_path (str): Source file path
            destination_path (str): Destination file path
        
        Returns:
            bool: True if successful
        """
        try:
            # Create destination directory if it doesn't exist
            Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(source_path, destination_path)
            self.logger.info(f"File moved from {source_path} to {destination_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error moving file from {source_path} to {destination_path}: {e}")
            return False
    
    def list_files(self, directory_path: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """
        List files in directory
        
        Args:
            directory_path (str): Directory path
            pattern (str): File pattern (glob)
            recursive (bool): Whether to search recursively
        
        Returns:
            List[str]: List of file paths
        """
        try:
            path_obj = Path(directory_path)
            
            if recursive:
                files = list(path_obj.rglob(pattern))
            else:
                files = list(path_obj.glob(pattern))
            
            file_paths = [str(f) for f in files if f.is_file()]
            
            self.logger.info(f"Found {len(file_paths)} files in {directory_path}")
            return file_paths
        
        except Exception as e:
            self.logger.error(f"Error listing files in {directory_path}: {e}")
            return []
    
    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes
        
        Args:
            file_path (str): File path
        
        Returns:
            int: File size in bytes
        """
        try:
            size = os.path.getsize(file_path)
            self.logger.info(f"File size of {file_path}: {size} bytes")
            return size
        
        except Exception as e:
            self.logger.error(f"Error getting file size for {file_path}: {e}")
            return -1
    
    def get_file_modification_time(self, file_path: str) -> datetime.datetime:
        """
        Get file modification time
        
        Args:
            file_path (str): File path
        
        Returns:
            datetime.datetime: File modification time
        """
        try:
            timestamp = os.path.getmtime(file_path)
            mod_time = datetime.datetime.fromtimestamp(timestamp)
            self.logger.info(f"File modification time of {file_path}: {mod_time}")
            return mod_time
        
        except Exception as e:
            self.logger.error(f"Error getting modification time for {file_path}: {e}")
            return None
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists
        
        Args:
            file_path (str): File path
        
        Returns:
            bool: True if file exists
        """
        exists = os.path.exists(file_path) and os.path.isfile(file_path)
        self.logger.info(f"File exists check for {file_path}: {exists}")
        return exists
    
    def directory_exists(self, directory_path: str) -> bool:
        """
        Check if directory exists
        
        Args:
            directory_path (str): Directory path
        
        Returns:
            bool: True if directory exists
        """
        exists = os.path.exists(directory_path) and os.path.isdir(directory_path)
        self.logger.info(f"Directory exists check for {directory_path}: {exists}")
        return exists
    
    def get_file_hash(self, file_path: str, algorithm: str = 'md5') -> str:
        """
        Get file hash
        
        Args:
            file_path (str): File path
            algorithm (str): Hash algorithm (md5, sha1, sha256)
        
        Returns:
            str: File hash
        """
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            file_hash = hash_obj.hexdigest()
            self.logger.info(f"File hash ({algorithm}) of {file_path}: {file_hash}")
            return file_hash
        
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def read_text_file(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Read text file content
        
        Args:
            file_path (str): File path
            encoding (str): File encoding
        
        Returns:
            str: File content
        """
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
            
            self.logger.info(f"Successfully read text file: {file_path}")
            return content
        
        except Exception as e:
            self.logger.error(f"Error reading text file {file_path}: {e}")
            return ""
    
    def write_text_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        Write text file content
        
        Args:
            file_path (str): File path
            content (str): Content to write
            encoding (str): File encoding
        
        Returns:
            bool: True if successful
        """
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as file:
                file.write(content)
            
            self.logger.info(f"Successfully wrote text file: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error writing text file {file_path}: {e}")
            return False
    
    def create_zip_archive(self, source_directory: str, zip_file_path: str) -> bool:
        """
        Create ZIP archive from directory
        
        Args:
            source_directory (str): Source directory path
            zip_file_path (str): ZIP file path
        
        Returns:
            bool: True if successful
        """
        try:
            # Create directory if it doesn't exist
            Path(zip_file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_directory)
                        zipf.write(file_path, arcname)
            
            self.logger.info(f"Successfully created ZIP archive: {zip_file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating ZIP archive {zip_file_path}: {e}")
            return False
    
    def extract_zip_archive(self, zip_file_path: str, extract_to: str) -> bool:
        """
        Extract ZIP archive
        
        Args:
            zip_file_path (str): ZIP file path
            extract_to (str): Extraction directory
        
        Returns:
            bool: True if successful
        """
        try:
            # Create directory if it doesn't exist
            Path(extract_to).mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_file_path, 'r') as zipf:
                zipf.extractall(extract_to)
            
            self.logger.info(f"Successfully extracted ZIP archive to: {extract_to}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error extracting ZIP archive {zip_file_path}: {e}")
            return False
    
    def create_temp_file(self, suffix: str = None, prefix: str = None, text: bool = True) -> str:
        """
        Create temporary file
        
        Args:
            suffix (str): File suffix
            prefix (str): File prefix
            text (bool): Whether file is text mode
        
        Returns:
            str: Temporary file path
        """
        try:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=suffix,
                prefix=prefix,
                mode='w+t' if text else 'w+b',
                delete=False
            )
            temp_file.close()
            
            self.logger.info(f"Created temporary file: {temp_file.name}")
            return temp_file.name
        
        except Exception as e:
            self.logger.error(f"Error creating temporary file: {e}")
            return ""
    
    def create_temp_directory(self, suffix: str = None, prefix: str = None) -> str:
        """
        Create temporary directory
        
        Args:
            suffix (str): Directory suffix
            prefix (str): Directory prefix
        
        Returns:
            str: Temporary directory path
        """
        try:
            temp_dir = tempfile.mkdtemp(suffix=suffix, prefix=prefix)
            self.logger.info(f"Created temporary directory: {temp_dir}")
            return temp_dir
        
        except Exception as e:
            self.logger.error(f"Error creating temporary directory: {e}")
            return ""

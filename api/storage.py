from google.cloud import storage
from typing import BinaryIO
import os
from dotenv import load_dotenv

load_dotenv()

class GCSStorage:
    """Google Cloud Storage wrapper"""
    
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME", "codeaudit-submissions")
        
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
        except Exception as e:
            print(f"Warning: Could not initialize GCS client: {e}")
            print("Using local file system as fallback")
            self.client = None
            self.bucket = None
    
    def upload_file(self, file_content: BinaryIO, destination_path: str) -> str:
        """
        Upload file to GCS and return the GCS URL
        """
        if not self.client:
            # Fallback to local storage
            return self._save_local(file_content, destination_path)
        
        try:
            blob = self.bucket.blob(destination_path)
            
            # Reset file pointer to beginning
            if hasattr(file_content, 'seek'):
                file_content.seek(0)
            
            blob.upload_from_file(file_content, rewind=True)
            
            return f"gs://{self.bucket_name}/{destination_path}"
        
        except Exception as e:
            print(f"Error uploading to GCS: {e}")
            return self._save_local(file_content, destination_path)
    
    def download_file(self, source_path: str) -> bytes:
        """
        Download file from GCS
        """
        if not self.client:
            # Fallback to local storage
            return self._load_local(source_path)
        
        try:
            blob = self.bucket.blob(source_path)
            return blob.download_as_bytes()
        
        except Exception as e:
            print(f"Error downloading from GCS: {e}")
            return self._load_local(source_path)
    
    def _save_local(self, file_content: BinaryIO, destination_path: str) -> str:
        """
        Fallback: Save file locally
        """
        local_dir = "/tmp/codeaudit-storage"
        os.makedirs(local_dir, exist_ok=True)
        
        local_path = os.path.join(local_dir, destination_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        if hasattr(file_content, 'seek'):
            file_content.seek(0)
        
        with open(local_path, 'wb') as f:
            f.write(file_content.read())
        
        return f"file://{local_path}"
    
    def _load_local(self, source_path: str) -> bytes:
        """
        Fallback: Load file from local storage
        """
        local_dir = "/tmp/codeaudit-storage"
        local_path = os.path.join(local_dir, source_path)
        
        with open(local_path, 'rb') as f:
            return f.read()

def get_storage_client():
    """Get storage client instance"""
    return GCSStorage()

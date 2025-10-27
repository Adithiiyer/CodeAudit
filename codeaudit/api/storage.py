from google.cloud import storage
from typing import BinaryIO
import os

class GCSStorage:
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(bucket_name)
    
    def upload_file(self, file_content: BinaryIO, destination_path: str) -> str:
        """
        Upload file to GCS and return the public URL
        """
        blob = self.bucket.blob(destination_path)
        blob.upload_from_file(file_content, rewind=True)
        
        return f"gs://{self.bucket_name}/{destination_path}"
    
    def download_file(self, source_path: str) -> bytes:
        """
        Download file from GCS
        """
        blob = self.bucket.blob(source_path)
        return blob.download_as_bytes()

# Initialize storage (will use env variable)
def get_storage_client():
    bucket_name = os.getenv("GCS_BUCKET_NAME", "codeaudit-submissions")
    return GCSStorage(bucket_name)
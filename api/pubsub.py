from google.cloud import pubsub_v1
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class PubSubPublisher:
    """Pub/Sub publisher for job queue"""
    
    def __init__(self, project_id: str = None, topic_name: str = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.topic_name = topic_name or os.getenv("PUBSUB_TOPIC", "code-review-jobs")
        
        try:
            self.publisher = pubsub_v1.PublisherClient()
            self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
        except Exception as e:
            print(f"Warning: Could not initialize Pub/Sub: {e}")
            self.publisher = None
            self.topic_path = None
    
    def publish_job(self, submission_id: str, file_path: str, language: str) -> str:
        """
        Publish a code review job to Pub/Sub
        """
        if not self.publisher:
            print(f"Pub/Sub not available. Job {submission_id} would be published.")
            return f"mock-message-id-{submission_id}"
        
        message = {
            "submission_id": submission_id,
            "file_path": file_path,
            "language": language,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            message_bytes = json.dumps(message).encode("utf-8")
            future = self.publisher.publish(self.topic_path, message_bytes)
            
            message_id = future.result(timeout=10)
            print(f"Published message {message_id} for submission {submission_id}")
            return message_id
        
        except Exception as e:
            print(f"Error publishing to Pub/Sub: {e}")
            return None

def get_pubsub_client():
    """Get Pub/Sub publisher client instance"""
    return PubSubPublisher()

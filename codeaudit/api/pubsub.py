from google.cloud import pubsub_v1
import json
import os

class PubSubPublisher:
    def __init__(self, project_id: str, topic_name: str):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_name)
    
    def publish_job(self, submission_id: str, file_path: str, language: str):
        """
        Publish a code review job to Pub/Sub
        """
        message = {
            "submission_id": submission_id,
            "file_path": file_path,
            "language": language,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        message_bytes = json.dumps(message).encode("utf-8")
        future = self.publisher.publish(self.topic_path, message_bytes)
        
        return future.result()

def get_pubsub_client():
    project_id = os.getenv("GCP_PROJECT_ID", "codeaudit-project")
    topic_name = os.getenv("PUBSUB_TOPIC", "code-review-jobs")
    return PubSubPublisher(project_id, topic_name)
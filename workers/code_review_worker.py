from google.cloud import pubsub_v1, storage
from concurrent.futures import TimeoutError
import json
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import SessionLocal
from database.models import Submission, ReviewResult, CustomRule
from agents.language_router import LanguageRouter
from agents.review_agent import CodeReviewAgent
from agents.security_agent import SecurityAgent
from agents.refactoring_agent import RefactoringAgent
from agents.custom_rules_engine import CustomRulesEngine

load_dotenv()

class CodeReviewWorker:
    """Worker that processes code review jobs from Pub/Sub"""
    
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.subscription_id = os.getenv("PUBSUB_SUBSCRIPTION", "code-review-workers")
        
        # Initialize Pub/Sub subscriber
        try:
            self.subscriber = pubsub_v1.SubscriberClient()
            self.subscription_path = self.subscriber.subscription_path(
                self.project_id, self.subscription_id
            )
        except Exception as e:
            print(f"Warning: Could not initialize Pub/Sub subscriber: {e}")
            self.subscriber = None
        
        # Initialize storage client
        try:
            self.storage_client = storage.Client()
        except Exception as e:
            print(f"Warning: Could not initialize storage client: {e}")
            self.storage_client = None
        
        # Initialize analyzers and agents
        self.language_router = LanguageRouter()
        self.review_agent = CodeReviewAgent()
        self.security_agent = SecurityAgent()
        self.refactoring_agent = RefactoringAgent()
        
        print("CodeReviewWorker initialized")
    
    def callback(self, message: pubsub_v1.subscriber.message.Message) -> None:
        """
        Process a single code review job
        """
        try:
            # Parse message
            data = json.loads(message.data.decode("utf-8"))
            submission_id = data["submission_id"]
            file_path = data["file_path"]
            language = data.get("language", "unknown")
            
            print(f"Processing submission: {submission_id}")
            
            # Download code from GCS
            code_content = self._download_from_gcs(file_path)
            
            if not code_content:
                print(f"Failed to download code for {submission_id}")
                self._update_submission_status(submission_id, "failed")
                message.ack()
                return
            
            # Update status to processing
            self._update_submission_status(submission_id, "processing")
            
            # Run static analysis using language router
            static_results = self.language_router.analyze(
                code_content,
                file_path,
                language
            )
            
            print(f"Static analysis complete for {submission_id}")
            
            # Get custom rules for this submission
            db = SessionLocal()
            custom_rules = db.query(CustomRule).filter(
                CustomRule.enabled == True
            ).all()
            
            # Convert to dict format
            rules_list = [
                {
                    'name': r.name,
                    'rule_type': r.rule_type,
                    'language': r.language,
                    'pattern': r.pattern,
                    'severity': r.severity,
                    'message': r.message,
                    'enabled': r.enabled,
                    'config': r.config
                }
                for r in custom_rules
            ]
            db.close()
            
            # Run custom rules engine
            if rules_list:
                rules_engine = CustomRulesEngine(rules_list)
                custom_violations = rules_engine.check_rules(
                    code_content,
                    static_results.get('language', language),
                    file_path
                )
                static_results['custom_rules'] = custom_violations
                print(f"Custom rules checked: {len(custom_violations)} violations")
            
            # Run AI agents
            print(f"Running AI review for {submission_id}")
            review_results = self.review_agent.process(code_content, static_results)
            
            print(f"Running security analysis for {submission_id}")
            security_results = self.security_agent.process(code_content, static_results)
            
            print(f"Running refactoring analysis for {submission_id}")
            refactoring_results = self.refactoring_agent.process(code_content, static_results)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                review_results, security_results, static_results
            )
            
            # Generate summary
            summary = self._generate_summary(
                review_results, security_results, refactoring_results, overall_score
            )
            
            # Save results to database
            self._save_results(
                submission_id,
                static_results,
                review_results,
                security_results,
                refactoring_results,
                overall_score,
                summary
            )
            
            # Update status to completed
            self._update_submission_status(submission_id, "completed")
            
            message.ack()
            print(f"✓ Completed submission: {submission_id} (Score: {overall_score}/100)")
            
        except Exception as e:
            print(f"Error processing message: {e}")
            import traceback
            traceback.print_exc()
            
            # Update status to failed
            try:
                submission_id = json.loads(message.data.decode("utf-8"))["submission_id"]
                self._update_submission_status(submission_id, "failed")
            except:
                pass
            
            message.nack()
    
    def _download_from_gcs(self, gcs_path: str) -> str:
        """Download file content from GCS"""
        try:
            # Handle both gs:// and regular paths
            if gcs_path.startswith("gs://"):
                path_parts = gcs_path.replace("gs://", "").split("/", 1)
                bucket_name = path_parts[0]
                blob_path = path_parts[1]
            else:
                bucket_name = os.getenv("GCS_BUCKET_NAME", "codeaudit-submissions")
                blob_path = gcs_path
            
            if self.storage_client:
                bucket = self.storage_client.bucket(bucket_name)
                blob = bucket.blob(blob_path)
                content = blob.download_as_bytes()
                return content.decode('utf-8')
            else:
                # Fallback to local storage
                local_path = f"/tmp/codeaudit-storage/{blob_path}"
                with open(local_path, 'r') as f:
                    return f.read()
        
        except Exception as e:
            print(f"Error downloading from GCS: {e}")
            return None
    
    def _update_submission_status(self, submission_id: str, status: str):
        """Update submission status in database"""
        try:
            db = SessionLocal()
            submission = db.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            
            if submission:
                submission.status = status
                db.commit()
            
            db.close()
        except Exception as e:
            print(f"Error updating submission status: {e}")
    
    def _calculate_overall_score(self, review, security, static) -> float:
        """Calculate weighted overall score"""
        review_score = review.get("overall_score", 70)
        security_score = security.get("security_score", 75)
        mi_score = static.get("maintainability_index", 65)
        
        # Weighted average: 40% review, 40% security, 20% maintainability
        overall = (review_score * 0.4) + (security_score * 0.4) + (mi_score * 0.2)
        return round(overall, 2)
    
    def _generate_summary(self, review, security, refactoring, overall_score) -> str:
        """Generate a text summary of the review"""
        issues_count = len(review.get("issues", []))
        vuln_count = len(security.get("vulnerabilities", []))
        
        summary_parts = [
            f"Overall Score: {overall_score}/100",
            f"Found {issues_count} code quality issues and {vuln_count} security concerns."
        ]
        
        if overall_score >= 80:
            summary_parts.append("The code is of good quality with minor improvements needed.")
        elif overall_score >= 60:
            summary_parts.append("The code is acceptable but has room for improvement.")
        else:
            summary_parts.append("The code needs significant improvements.")
        
        return " ".join(summary_parts)
    
    def _save_results(
        self,
        submission_id,
        static,
        review,
        security,
        refactoring,
        overall_score,
        summary
    ):
        """Save analysis results to database"""
        try:
            db = SessionLocal()
            
            # Count total issues
            total_issues = (
                len(review.get("issues", [])) +
                len(security.get("vulnerabilities", [])) +
                len(static.get("custom_rules", []))
            )
            
            result = ReviewResult(
                submission_id=submission_id,
                quality_score=review.get("overall_score"),
                security_score=security.get("security_score"),
                maintainability_score=static.get("maintainability_index"),
                overall_score=overall_score,
                static_analysis=static,
                ai_review=review,
                security_analysis=security,
                refactoring_suggestions=refactoring,
                summary=summary,
                issues_count=total_issues
            )
            
            db.add(result)
            db.commit()
            db.close()
            
            print(f"Results saved for {submission_id}")
        
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def start(self):
        """Start listening for messages"""
        if not self.subscriber:
            print("Pub/Sub subscriber not available. Running in mock mode.")
            print("In production, this would listen for jobs from Pub/Sub.")
            return
        
        print(f"Worker started. Listening to {self.subscription_path}")
        
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=self.callback
        )
        
        print(f"Listening for messages on {self.subscription_path}...")
        
        try:
            # Block until the subscription is cancelled
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            print("\nWorker stopped")
        except Exception as e:
            print(f"Error in streaming pull: {e}")
            streaming_pull_future.cancel()

if __name__ == "__main__":
    worker = CodeReviewWorker()
    worker.start()

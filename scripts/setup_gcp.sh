#!/bin/bash
# Google Cloud Platform setup script for CodeAudit

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

PROJECT_ID=${GCP_PROJECT_ID:-"codeaudit-project"}
REGION=${GCP_REGION:-"us-central1"}
BUCKET_NAME=${GCS_BUCKET_NAME:-"codeaudit-submissions"}

echo "Setting up CodeAudit on Google Cloud Platform"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set the project
echo "Setting active project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    pubsub.googleapis.com \
    storage.googleapis.com \
    sqladmin.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com

# Create GCS bucket
echo "Creating Cloud Storage bucket..."
gsutil mb -p $PROJECT_ID -l $REGION gs://$BUCKET_NAME 2>/dev/null || echo "Bucket already exists"

# Set bucket lifecycle (auto-delete old files after 90 days)
echo '{
  "lifecycle": {
    "rule": [{
      "action": {"type": "Delete"},
      "condition": {"age": 90}
    }]
  }
}' > /tmp/lifecycle.json

gsutil lifecycle set /tmp/lifecycle.json gs://$BUCKET_NAME
rm /tmp/lifecycle.json

# Create Pub/Sub topic
echo "Creating Pub/Sub topic..."
gcloud pubsub topics create code-review-jobs 2>/dev/null || echo "Topic already exists"

# Create Pub/Sub subscription
echo "Creating Pub/Sub subscription..."
gcloud pubsub subscriptions create code-review-workers \
    --topic=code-review-jobs \
    --ack-deadline=600 \
    --message-retention-duration=7d 2>/dev/null || echo "Subscription already exists"

# Create Cloud SQL instance (optional - comment out if using local DB)
read -p "Do you want to create a Cloud SQL instance? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating Cloud SQL instance (this may take several minutes)..."
    gcloud sql instances create codeaudit-db \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region=$REGION \
        --root-password=$(openssl rand -base64 32) 2>/dev/null || echo "Instance already exists"
    
    echo "Creating database..."
    gcloud sql databases create codeaudit --instance=codeaudit-db 2>/dev/null || echo "Database already exists"
fi

echo ""
echo "✓ Google Cloud Platform setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Run 'python scripts/init_db.py' to initialize the database"
echo "3. Deploy services with 'bash scripts/deploy.sh'"

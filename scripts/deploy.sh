#!/bin/bash
# Deployment script for CodeAudit

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

PROJECT_ID=${GCP_PROJECT_ID:-"codeaudit-project"}
REGION=${GCP_REGION:-"us-central1"}

echo "Deploying CodeAudit to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Build and push API container
echo "Building API container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/codeaudit-api -f Dockerfile.api .

echo "Deploying API to Cloud Run..."
gcloud run deploy codeaudit-api \
    --image gcr.io/$PROJECT_ID/codeaudit-api \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCS_BUCKET_NAME=$GCS_BUCKET_NAME,ENV=production" \
    --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,DB_PASSWORD=DB_PASSWORD:latest"

# Build and push worker container
echo "Building worker container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/codeaudit-worker -f Dockerfile.worker .

# Deploy worker as Cloud Run Job
echo "Deploying worker..."
gcloud run jobs create codeaudit-worker \
    --image gcr.io/$PROJECT_ID/codeaudit-worker \
    --region $REGION \
    --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCS_BUCKET_NAME=$GCS_BUCKET_NAME,ENV=production" \
    --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,DB_PASSWORD=DB_PASSWORD:latest" \
    2>/dev/null || echo "Worker job already exists"

# Get the API URL
API_URL=$(gcloud run services describe codeaudit-api --region $REGION --format='value(status.url)')

echo ""
echo "✓ Deployment complete!"
echo ""
echo "API URL: $API_URL"
echo "API Docs: $API_URL/docs"
echo ""
echo "To execute a worker job:"
echo "gcloud run jobs execute codeaudit-worker --region $REGION"

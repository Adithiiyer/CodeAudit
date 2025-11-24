# CodeAudit - Complete Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Google Cloud Setup](#google-cloud-setup)
4. [Running Locally](#running-locally)
5. [Deploying to Production](#deploying-to-production)
6. [Testing the System](#testing-the-system)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)
- **PostgreSQL 14+** (for local development) - [Download](https://www.postgresql.org/download/)
- **Google Cloud SDK** - [Install](https://cloud.google.com/sdk/docs/install)

### Required Accounts
- **Google Cloud Account** with billing enabled
- **OpenAI API Account** - [Get API Key](https://platform.openai.com/api-keys)

---

## Local Development Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/codeaudit.git
cd codeaudit
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Set Up Local Database

```bash
# Install PostgreSQL (if not already installed)
# On macOS:
brew install postgresql@14
brew services start postgresql@14

# On Ubuntu/Debian:
sudo apt-get install postgresql-14

# Create database
createdb codeaudit

# Or using psql:
psql postgres
CREATE DATABASE codeaudit;
\q
```

### Step 4: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required .env variables for local development:**
```bash
ENV=development
DATABASE_URL=postgresql://postgres:password@localhost/codeaudit
OPENAI_API_KEY=your_openai_api_key_here
GCS_BUCKET_NAME=codeaudit-submissions-local
```

### Step 5: Initialize Database

```bash
python scripts/init_db.py
```

You should see:
```
✓ Database tables created successfully
✓ Created demo user (email: demo@codeaudit.com, password: demo123)
✓ Created 2 sample custom rules
✓ Database initialization complete!
```

### Step 6: Set Up Frontend

```bash
cd frontend
npm install
cd ..
```

---

## Google Cloud Setup

### Step 1: Create Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create new project
gcloud projects create codeaudit-project --name="CodeAudit"

# Set active project
gcloud config set project codeaudit-project

# Link billing account (required)
# Go to: https://console.cloud.google.com/billing
```

### Step 2: Run Setup Script

```bash
# Make script executable
chmod +x scripts/setup_gcp.sh

# Run setup
bash scripts/setup_gcp.sh
```

This script will:
- Enable required Google Cloud APIs
- Create Cloud Storage bucket
- Create Pub/Sub topic and subscription
- Optionally create Cloud SQL instance

### Step 3: Set Up Secrets

```bash
# Store OpenAI API key as secret
echo -n "your_openai_api_key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Store database password as secret
echo -n "your_db_password" | gcloud secrets create DB_PASSWORD --data-file=-

# Grant Cloud Run access to secrets
PROJECT_NUMBER=$(gcloud projects describe codeaudit-project --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

---

## Running Locally

### Terminal 1: Start the API

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete.
```

### Terminal 2: Start the Worker (Optional for local testing)

```bash
# Activate virtual environment
source venv/bin/activate

# Start worker
python workers/code_review_worker.py
```

### Terminal 3: Start the Frontend

```bash
cd frontend
npm start
```

Browser will open at `http://localhost:3000`

### Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8080/docs
- **API Health Check**: http://localhost:8080/health

---

## Deploying to Production

### Step 1: Build and Deploy

```bash
# Make deploy script executable
chmod +x scripts/deploy.sh

# Deploy to Google Cloud Run
bash scripts/deploy.sh
```

### Step 2: Verify Deployment

```bash
# Get API URL
API_URL=$(gcloud run services describe codeaudit-api --region us-central1 --format='value(status.url)')

# Test API
curl $API_URL/health

# Visit API docs
echo "$API_URL/docs"
```

### Step 3: Set Up Continuous Worker

```bash
# Create Cloud Scheduler job to trigger worker every minute
gcloud scheduler jobs create http code-review-trigger \
    --location=us-central1 \
    --schedule="* * * * *" \
    --uri="$API_URL/api/v1/trigger-worker" \
    --http-method=POST
```

---

## Testing the System

### Test 1: Submit a Simple Python File

```bash
# Create a test file
cat > test.py << 'EOF'
def calculate_sum(a, b):
    """Calculate sum of two numbers"""
    result = a + b
    print(f"Sum is: {result}")
    return result

x = 10
y = 20
calculate_sum(x, y)
EOF

# Submit via curl
curl -X POST http://localhost:8080/api/v1/submit \
    -F "file=@test.py" \
    -F "language=python"
```

Expected response:
```json
{
  "submission_id": "uuid-here",
  "status": "pending",
  "message": "Code submitted successfully"
}
```

### Test 2: Check Results

```bash
# Replace with your submission_id
SUBMISSION_ID="uuid-from-above"

# Wait a few seconds, then check results
curl http://localhost:8080/api/v1/results/$SUBMISSION_ID
```

### Test 3: Submit a Batch (Zip File)

```bash
# Create multiple test files
mkdir test_project
cat > test_project/main.py << 'EOF'
def main():
    print("Hello World")
EOF

cat > test_project/utils.py << 'EOF'
def helper():
    return "Helper"
EOF

# Create zip
zip -r test_project.zip test_project/

# Submit batch
curl -X POST http://localhost:8080/api/v1/submit-batch \
    -F "file=@test_project.zip" \
    -F "project_name=TestProject"
```

### Test 4: Use the Web Interface

1. Open browser to `http://localhost:3000`
2. Click "Submit Code"
3. Upload a Python file
4. Wait for processing
5. View results in dashboard

---

## Troubleshooting

### Problem: Database connection errors

**Solution:**
```bash
# Check if PostgreSQL is running
# macOS:
brew services list | grep postgresql

# Ubuntu:
sudo systemctl status postgresql

# Test connection
psql -d codeaudit -c "SELECT 1"
```

### Problem: OpenAI API errors

**Solution:**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
    -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Problem: Google Cloud permissions

**Solution:**
```bash
# Re-authenticate
gcloud auth application-default login

# Check current project
gcloud config get-value project

# List enabled APIs
gcloud services list --enabled
```

### Problem: Worker not processing jobs

**Solution:**
```bash
# Check Pub/Sub topic exists
gcloud pubsub topics list

# Check subscription exists
gcloud pubsub subscriptions list

# Manually pull a message to test
gcloud pubsub subscriptions pull code-review-workers --limit=1
```

### Problem: Static analyzers not working

**Solution:**
```bash
# Reinstall analysis tools
pip install pylint bandit radon --force-reinstall

# Test pylint
pylint --version

# Test bandit
bandit --version
```

---

## Common Commands

### Development

```bash
# Start everything in one terminal (requires tmux)
tmux new-session \; \
  send-keys 'uvicorn api.main:app --reload' C-m \; \
  split-window -h \; \
  send-keys 'cd frontend && npm start' C-m \;
```

### Database Management

```bash
# View all submissions
python -c "from database import SessionLocal, Submission; db = SessionLocal(); print([s.filename for s in db.query(Submission).all()])"

# Clear all data (careful!)
python scripts/init_db.py --reset
```

### Deployment

```bash
# Redeploy only API
gcloud builds submit --tag gcr.io/codeaudit-project/codeaudit-api -f Dockerfile.api .
gcloud run deploy codeaudit-api --image gcr.io/codeaudit-project/codeaudit-api

# View logs
gcloud run logs read codeaudit-api --limit=50

# Execute worker manually
gcloud run jobs execute codeaudit-worker --region us-central1
```

---

## Next Steps

1. **Customize Rules**: Add your own custom review rules via the API or database
2. **Extend Languages**: Add more static analyzers for additional languages
3. **Improve Agents**: Fine-tune the AI prompts for better reviews
4. **Add Authentication**: Implement JWT-based user authentication
5. **Set Up Monitoring**: Add Prometheus metrics and alerting
6. **Scale Workers**: Deploy multiple worker instances for high volume

---

## Support

- **Documentation**: See README.md
- **Issues**: Open issues on GitHub
- **API Reference**: http://localhost:8080/docs

## License

MIT License - see LICENSE file for details

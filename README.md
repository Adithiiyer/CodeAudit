# CodeAudit - AI-Powered Code Review Platform

CodeAudit is a cloud-based AI-powered service that automatically reviews and improves code quality at scale.

## Features

- 🤖 **AI-Powered Analysis**: Multiple specialized agents for review, security, and refactoring
- 🔍 **Static Analysis**: Comprehensive code quality checks using industry-standard tools
- 🌐 **Multi-Language Support**: Python, JavaScript, Java, and more
- 📊 **Quality Scoring**: Transparent metrics for every submission
- 💬 **Interactive Chat**: Ask questions about your code review results
- 📈 **Trend Tracking**: Monitor code quality improvements over time
- ⚙️ **Custom Rules**: Define your own review criteria
- 📦 **Batch Processing**: Handle entire projects at once

## Quick Start

### Prerequisites

- Python 3.10+
- Google Cloud Account
- OpenAI API Key
- Node.js 16+ (for frontend)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/codeaudit.git
cd codeaudit
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Set up Google Cloud**
```bash
gcloud init
gcloud config set project codeaudit-project

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Create resources
./scripts/setup_gcp.sh
```

5. **Initialize database**
```bash
python scripts/init_db.py
```

6. **Run the API**
```bash
python -m uvicorn api.main:app --reload
```

7. **Set up frontend**
```bash
cd frontend
npm install
npm start
```

### Local Development

**Run API:**
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

**Run Worker:**
```bash
python workers/code_review_worker.py
```

**Run Tests:**
```bash
pytest tests/
```

## Architecture

```
┌─────────────┐
│   Client    │
│  (Web/API)  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   FastAPI       │
│   API Server    │
└────────┬────────┘
         │
         ├──────────────┬─────────────┬──────────────┐
         ▼              ▼             ▼              ▼
   ┌─────────┐   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │   GCS   │   │ Pub/Sub  │  │ Cloud SQL│  │ Vertex AI│
   │ Storage │   │  Queue   │  │ Database │  │   LLM    │
   └─────────┘   └────┬─────┘  └──────────┘  └──────────┘
                      │
                      ▼
              ┌──────────────┐
              │   Workers    │
              │  (Agents)    │
              └──────────────┘
```

## API Endpoints

### Submissions
- `POST /api/v1/submit` - Submit single file
- `POST /api/v1/submit-batch` - Submit zip file
- `GET /api/v1/results/{submission_id}` - Get results
- `GET /api/v1/batch/{batch_id}/status` - Batch status

### Projects & Trends
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{project_id}/trends` - Get trends

### Custom Rules
- `POST /api/v1/rules` - Create custom rule
- `GET /api/v1/rules` - List rules
- `PUT /api/v1/rules/{rule_id}/toggle` - Enable/disable rule

### Chat
- `POST /api/v1/chat/start` - Start chat session
- `POST /api/v1/chat/{session_id}/message` - Send message
- `GET /api/v1/chat/{session_id}/history` - Get history

## Deployment

### Docker Build
```bash
docker build -f Dockerfile.api -t gcr.io/codeaudit-project/api .
docker build -f Dockerfile.worker -t gcr.io/codeaudit-project/worker .
docker build -f Dockerfile.frontend -t gcr.io/codeaudit-project/frontend .
```

### Deploy to Cloud Run
```bash
gcloud run deploy codeaudit-api \
  --image gcr.io/codeaudit-project/api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuration

See `.env.example` for all configuration options.

## License

MIT License - See LICENSE file for details

## Contributors

- Ishani Mody
- Adithi Iyer Mukund

## Support

For issues and questions, please open a GitHub issue.

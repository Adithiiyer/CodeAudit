# CodeAudit - Project File Structure

## 📁 Complete File Listing

```
codeaudit/
├── README.md                          # Project overview and introduction
├── SETUP.md                           # Comprehensive setup guide
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                        # Git ignore rules
│
├── api/                              # FastAPI Application
│   ├── __init__.py
│   ├── main.py                       # Main API with all endpoints
│   ├── storage.py                    # Google Cloud Storage wrapper
│   └── pubsub.py                     # Google Pub/Sub wrapper
│
├── agents/                           # AI Agents
│   ├── __init__.py
│   ├── base_agent.py                 # Base agent class
│   ├── review_agent.py               # Code review agent
│   ├── security_agent.py             # Security analysis agent
│   ├── refactoring_agent.py          # Refactoring suggestions agent
│   ├── language_router.py            # Multi-language routing
│   ├── chat_agent.py                 # Interactive Q&A agent
│   └── custom_rules_engine.py        # Custom rules evaluation
│
├── static-analyzers/                 # Static Code Analysis
│   ├── __init__.py
│   ├── python_analyzer.py            # Python static analysis
│   ├── javascript_analyzer.py        # JavaScript/TypeScript analysis
│   └── java_analyzer.py              # Java analysis
│
├── database/                         # Database Layer
│   ├── __init__.py
│   ├── models.py                     # SQLAlchemy models
│   └── connection.py                 # Database connection manager
│
├── workers/                          # Background Workers
│   └── code_review_worker.py        # Main worker for processing jobs
│
├── scripts/                          # Utility Scripts
│   ├── init_db.py                    # Database initialization
│   ├── setup_gcp.sh                  # Google Cloud setup
│   ├── deploy.sh                     # Deployment script
│   └── quickstart.sh                 # Quick start for local dev
│
├── tests/                            # Test Files
│   └── sample_code.py                # Sample code for testing
│
├── frontend/                         # React Frontend
│   ├── package.json                  # Node dependencies
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js                    # Main React app
│       ├── App.css
│       ├── index.js
│       └── components/
│           ├── Dashboard.js          # Main dashboard
│           ├── SubmitCode.js         # Code submission form
│           ├── ViewResults.js        # Results display
│           ├── TrendsChart.js        # Trends visualization
│           └── ChatInterface.js      # Interactive chat
│
├── Dockerfile.api                    # Docker image for API
├── Dockerfile.worker                 # Docker image for worker
└── Dockerfile.frontend               # Docker image for frontend

```

## 🚀 Quick Start Commands

### 1. Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd codeaudit

# Quick setup (creates venv, installs deps, initializes DB)
bash scripts/quickstart.sh
```

### 2. Run Locally
```bash
# Terminal 1: API
source venv/bin/activate
uvicorn api.main:app --reload --port 8080

# Terminal 2: Worker (optional for local testing)
source venv/bin/activate
python workers/code_review_worker.py

# Terminal 3: Frontend
cd frontend
npm install
npm start
```

### 3. Deploy to Google Cloud
```bash
# Setup Google Cloud
bash scripts/setup_gcp.sh

# Deploy services
bash scripts/deploy.sh
```

## 📋 Key Features Implemented

### ✅ Core Features
- [x] Single file code submission
- [x] Batch processing (zip files)
- [x] Multi-language support (Python, JavaScript, Java)
- [x] Static code analysis
- [x] AI-powered code review
- [x] Security vulnerability detection
- [x] Code quality scoring

### ✅ Advanced Features
- [x] Custom rules engine
- [x] Interactive chat with reviews
- [x] Trend tracking over time
- [x] Project organization
- [x] Dashboard with visualizations
- [x] Batch reporting

### ✅ Infrastructure
- [x] FastAPI REST API
- [x] Google Cloud Storage integration
- [x] Pub/Sub job queue
- [x] PostgreSQL database
- [x] Cloud SQL support
- [x] Docker containers
- [x] Cloud Run deployment

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database
- **OpenAI API** - GPT-4 for code analysis
- **Pylint, Bandit, Radon** - Python static analysis
- **ESLint** - JavaScript analysis

### Frontend
- **React** - UI framework
- **Material-UI** - Component library
- **Recharts** - Data visualization
- **Axios** - HTTP client

### Infrastructure
- **Google Cloud Run** - Serverless containers
- **Google Cloud Storage** - File storage
- **Google Pub/Sub** - Message queue
- **Cloud SQL (PostgreSQL)** - Managed database
- **Docker** - Containerization

## 📚 Documentation

- **README.md** - Project overview, features, architecture
- **SETUP.md** - Complete setup guide with troubleshooting
- **API Docs** - Auto-generated at `/docs` endpoint

## 🧪 Testing

### Test the API
```bash
# Health check
curl http://localhost:8080/health

# Submit code
curl -X POST http://localhost:8080/api/v1/submit \
  -F "file=@tests/sample_code.py"

# Check results
curl http://localhost:8080/api/v1/results/{submission_id}
```

### Use Sample Code
```bash
# Submit the sample problematic code
curl -X POST http://localhost:8080/api/v1/submit \
  -F "file=@tests/sample_code.py" \
  -F "language=python"
```

## 🎯 API Endpoints Summary

### Submissions
- `POST /api/v1/submit` - Submit single file
- `POST /api/v1/submit-batch` - Submit zip file
- `GET /api/v1/results/{id}` - Get results
- `GET /api/v1/batch/{id}/status` - Batch status
- `GET /api/v1/batch/{id}/report` - Batch report

### Projects & Trends
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}/trends` - View trends
- `POST /api/v1/projects/{id}/record-metrics` - Record metrics

### Custom Rules
- `POST /api/v1/rules` - Create rule
- `GET /api/v1/rules` - List rules
- `PUT /api/v1/rules/{id}/toggle` - Enable/disable
- `DELETE /api/v1/rules/{id}` - Delete rule

### Chat
- `POST /api/v1/chat/start` - Start chat session
- `POST /api/v1/chat/{id}/message` - Send message
- `GET /api/v1/chat/{id}/history` - Get history
- `DELETE /api/v1/chat/{id}` - End session

### Dashboard
- `GET /api/v1/dashboard/stats` - Get statistics
- `GET /health` - Health check

## 💡 Usage Examples

### Python Example
```python
import requests

# Submit code
with open('my_code.py', 'rb') as f:
    response = requests.post(
        'http://localhost:8080/api/v1/submit',
        files={'file': f}
    )
submission_id = response.json()['submission_id']

# Get results
results = requests.get(
    f'http://localhost:8080/api/v1/results/{submission_id}'
).json()

print(f"Score: {results['overall_score']}/100")
```

### JavaScript Example
```javascript
// Submit code
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8080/api/v1/submit', {
  method: 'POST',
  body: formData
});

const { submission_id } = await response.json();

// Get results
const results = await fetch(
  `http://localhost:8080/api/v1/results/${submission_id}`
).then(r => r.json());

console.log(`Score: ${results.overall_score}/100`);
```

## 🔐 Security Notes

1. Never commit `.env` file
2. Use environment variables for secrets
3. Enable authentication in production
4. Restrict CORS origins in production
5. Use HTTPS in production
6. Rotate API keys regularly

## 📈 Performance Tips

1. Use Cloud SQL connection pooling
2. Enable Cloud CDN for frontend
3. Scale Cloud Run instances as needed
4. Monitor Pub/Sub queue depth
5. Implement rate limiting
6. Cache frequent queries

## 🤝 Contributing

This is a student project by Ishani Mody and Adithi Iyer Mukund.
For improvements or bug fixes, please follow standard Git workflow.

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for making code reviews better through AI**

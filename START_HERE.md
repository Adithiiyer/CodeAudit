# 🚀 START HERE - CodeAudit Setup Instructions

**Welcome to CodeAudit!** This guide will get you up and running in 10 minutes.

---

## ⚡ Super Quick Start (For the Impatient)

```bash
# 1. Setup everything
bash scripts/quickstart.sh

# 2. Add your OpenAI API key to .env file
nano .env  # Add OPENAI_API_KEY=your_key_here

# 3. Start the API
source venv/bin/activate
uvicorn api.main:app --reload --port 8080

# 4. Visit http://localhost:8080/docs
```

That's it! Your API is running. Open http://localhost:8080/docs in your browser.

---

## 📚 What You Just Built

CodeAudit is an **AI-powered code review platform** that:
- ✅ Analyzes code quality using static analysis + GPT-4
- ✅ Detects security vulnerabilities
- ✅ Suggests refactoring improvements
- ✅ Supports Python, JavaScript, and Java
- ✅ Provides interactive chat about your code
- ✅ Tracks code quality trends over time

---

## 🎯 Step-by-Step Setup

### Prerequisites Checklist

- [ ] Python 3.10+ installed (`python --version`)
- [ ] pip installed (`pip --version`)
- [ ] Git installed (`git --version`)
- [ ] OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

Optional for full features:
- [ ] PostgreSQL 14+ (for database)
- [ ] Node.js 16+ (for frontend)
- [ ] Google Cloud account (for deployment)

### Step 1: Get the Code

```bash
cd ~
# If you received a zip file
unzip codeaudit.zip
cd codeaudit

# OR if you have git repository
git clone <repository-url>
cd codeaudit
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install Python packages
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Use any text editor (nano, vim, VS Code, etc.)
nano .env
```

**Required changes in .env:**
```bash
OPENAI_API_KEY=your_actual_openai_api_key_here
```

**For local development without Google Cloud:**
```bash
ENV=development
DATABASE_URL=postgresql://postgres:password@localhost/codeaudit
```

**Don't have PostgreSQL?** No problem! SQLite will work for testing:
```bash
DATABASE_URL=sqlite:///./codeaudit.db
```

### Step 4: Initialize Database

```bash
python scripts/init_db.py
```

You should see success messages like:
```
✓ Database tables created successfully
✓ Created demo user
✓ Database initialization complete!
```

### Step 5: Start the API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete.
```

### Step 6: Test It!

**Option A: Use the Auto-Generated API Docs**
1. Open browser to http://localhost:8080/docs
2. Click "Try it out" on `/api/v1/submit`
3. Upload a Python file
4. Execute and get your submission_id

**Option B: Use curl**
```bash
# Create a test file
cat > test.py << 'EOF'
def hello(name):
    print(f"Hello {name}")
hello("World")
EOF

# Submit it
curl -X POST http://localhost:8080/api/v1/submit \
  -F "file=@test.py" \
  -F "language=python"
```

**Option C: Use the Sample File**
```bash
curl -X POST http://localhost:8080/api/v1/submit \
  -F "file=@tests/sample_code.py" \
  -F "language=python"
```

You'll get back:
```json
{
  "submission_id": "abc-123-xyz",
  "status": "pending",
  "message": "Code submitted successfully"
}
```

### Step 7: Get Results

Wait a few seconds, then check results:

```bash
# Replace with your actual submission_id
curl http://localhost:8080/api/v1/results/abc-123-xyz
```

You'll see detailed analysis including:
- Overall quality score (0-100)
- Security analysis
- Code issues and suggestions
- Refactoring recommendations

---

## 🎨 Optional: Start the Frontend

Want a nice UI? Run these commands in a **new terminal**:

```bash
cd frontend
npm install
npm start
```

Then open http://localhost:3000 in your browser!

---

## 🧪 Testing the System

### Test 1: Basic Submission
```bash
echo 'print("hello")' > simple.py
curl -X POST http://localhost:8080/api/v1/submit -F "file=@simple.py"
```

### Test 2: Batch Processing
```bash
# Create a small project
mkdir my_project
echo 'def func1(): pass' > my_project/file1.py
echo 'def func2(): pass' > my_project/file2.py
zip -r project.zip my_project/

# Submit the batch
curl -X POST http://localhost:8080/api/v1/submit-batch \
  -F "file=@project.zip" \
  -F "project_name=MyProject"
```

### Test 3: Interactive Chat
1. Submit a file and get the submission_id
2. Start a chat session:
```bash
curl -X POST "http://localhost:8080/api/v1/chat/start?submission_id=YOUR_ID"
```
3. Ask questions:
```bash
curl -X POST "http://localhost:8080/api/v1/chat/SESSION_ID/message?message=Why%20did%20I%20get%20a%20low%20score?"
```

---

## 📁 Project Structure

```
codeaudit/
├── api/              # FastAPI backend (main.py is the entry point)
├── agents/           # AI agents for review, security, etc.
├── static-analyzers/ # Code analysis tools
├── database/         # Database models and connections
├── workers/          # Background job processors
├── frontend/         # React UI (optional)
├── scripts/          # Setup and deployment scripts
└── tests/           # Sample files for testing
```

**Key files:**
- `api/main.py` - Main API with all endpoints
- `workers/code_review_worker.py` - Processes review jobs
- `agents/review_agent.py` - AI-powered code review
- `scripts/init_db.py` - Database setup

---

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError"
**Solution:** Make sure virtual environment is activated and dependencies are installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: "OpenAI API error"
**Solution:** Check your API key in .env file
```bash
# Verify it's set
grep OPENAI_API_KEY .env

# Test it
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

### Problem: "Database connection failed"
**Solution:** Either install PostgreSQL or use SQLite
```bash
# For SQLite (simpler for testing)
# Edit .env and change DATABASE_URL to:
DATABASE_URL=sqlite:///./codeaudit.db

# Then reinitialize
python scripts/init_db.py
```

### Problem: "Port 8080 already in use"
**Solution:** Use a different port
```bash
uvicorn api.main:app --reload --port 8081
```

### Problem: Worker not processing jobs
**Solution:** For local testing without Pub/Sub:
- The worker expects Google Pub/Sub
- For local development, you can manually call the analysis by importing the functions directly
- Or deploy to Google Cloud where Pub/Sub is available

---

## 📖 Next Steps

1. **Read the Full Documentation**
   - `README.md` - Project overview
   - `SETUP.md` - Detailed setup with Google Cloud
   - `PROJECT_INDEX.md` - Complete file listing

2. **Try Advanced Features**
   - Custom rules: Create your own code review rules
   - Batch processing: Submit entire projects
   - Trend tracking: Monitor code quality over time
   - Interactive chat: Ask questions about your reviews

3. **Deploy to Production**
   - Follow `SETUP.md` for Google Cloud deployment
   - Run `bash scripts/deploy.sh`

4. **Customize for Your Needs**
   - Modify AI prompts in `agents/` folder
   - Add support for more languages
   - Integrate with your CI/CD pipeline

---

## 💡 Quick Tips

1. **API Documentation**: Always available at http://localhost:8080/docs
2. **Sample Code**: Use `tests/sample_code.py` - it has intentional issues to test with
3. **Environment**: Keep `.env` file secure, never commit it
4. **Database**: Run `python scripts/init_db.py` anytime to reset
5. **Logs**: Watch the terminal where API is running for debugging

---

## 🆘 Need Help?

1. Check `SETUP.md` for detailed troubleshooting
2. Review API docs at `/docs` endpoint
3. Examine error messages in the terminal
4. Make sure all dependencies are installed
5. Verify .env file has correct settings

---

## 🎉 Success Checklist

- [ ] API running on http://localhost:8080
- [ ] Can access /docs page
- [ ] Can submit a file via curl or UI
- [ ] Can retrieve results
- [ ] Database initialized successfully

**If all checked: Congratulations! You're ready to use CodeAudit!** 🚀

---

**Authors:** Ishani Mody & Adithi Iyer Mukund

**License:** MIT

**Last Updated:** October 2025

# CodeAudit – AI-Powered Automated Code Review Platform  
### Team : Adithi Iyer Mukund & Ishani Mody

CodeAudit is an AI-driven automated code review system designed to analyze source code for **quality**, **security**, and **performance** issues.  
It combines **static analysis tools**, **custom rule-based checks**, and **Groq LLM (llama3-8b-8192 / 8-instant)** to provide deep semantic insights similar to a human reviewer.

This project helps developers and students get instant, consistent, and high-quality feedback on their code with a simple, intuitive UI.

---

## Features

###  Multi-Language Support
- Python (`.py`)
- JavaScript / TypeScript (`.js`, `.ts`)
- Java (`.java`)
- C++ (`.cpp`)
- Go (`.go`)
- `.zip` file uploads for project folders

### Three Submission Options
- Upload a file  
- Drag & drop  
- Paste code directly in editor  

### AI-Powered Code Review (Groq LLM)
- Code quality and readability insights  
- Security vulnerability detection  
- Performance & complexity evaluation  
- Optimization suggestions  
- Human-like reasoning & explanations  

###  Static Analysis Tools Integrated
- Python → **Pylint**, **Bandit**
- JavaScript → **ESLint**
- Custom checks → complexity, nested loops, variable naming, comments, maintainability

### Scoring System (0–100)
Weighted scoring mechanism:
- **40%** Quality  
- **40%** Security  
- **20%** Performance / Maintainability  

### Modern Frontend UI
- React + Material UI  
- Light/Dark theme support  
- Real-time polling of backend  
- Clean dashboard with results  

### Cloud-Ready Deployment
- Works on Google Cloud Run  
- Supports Cloud Storage integration  
- Fully containerized with Docker  

---

## System Architecture

```text
Frontend (React)
      ↓
FastAPI Backend (REST API)
      ↓
Static Analysis Engines
      ↓
Groq LLM (Semantic Review)
      ↓
SQLite Database
      ↓
Frontend Dashboard (Displays Results)

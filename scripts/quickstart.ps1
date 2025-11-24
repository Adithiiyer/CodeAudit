# Quick start script for CodeAudit local development (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "CodeAudit - Quick Start" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    
    # Check if .env.example exists
    if (Test-Path ".env.example") {
        Copy-Item "$(dirname "$0")/../.env.example" ".env"
    } else {
        # Create a basic .env file
        $envContent = @"
ENV=development
DATABASE_URL=sqlite:///./codeaudit.db
OPENAI_API_KEY=your_api_key_here
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
    }
    
    Write-Host "⚠️  Please edit .env and add your OPENAI_API_KEY before continuing" -ForegroundColor Yellow
    Write-Host "   Then run this script again." -ForegroundColor Yellow
    exit 1
}

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Green
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create virtual environment. Make sure Python is installed." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

Write-Host "Installing Python dependencies..." -ForegroundColor Green
pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies." -ForegroundColor Red
    exit 1
}

Write-Host "Initializing database..." -ForegroundColor Green
python scripts/init_db.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Database initialization may have failed. Continuing anyway..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start the API:" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   uvicorn api.main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "2. (Optional) Start the worker in another terminal:" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python workers/code_review_worker.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start the frontend in another terminal:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host "   npm start" -ForegroundColor Gray
Write-Host ""
Write-Host "Then visit: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8080/docs" -ForegroundColor Cyan
Write-Host ""

# MediaBoard AI - Windows Setup Script
# This script helps set up the MediaBoard AI application on Windows

Write-Host "🎨 MediaBoard AI - Windows Setup" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan

# Check Python version
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created!" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green

# Setup environment file
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "📋 Created .env file from .env.example" -ForegroundColor Green
    } else {
        # Create basic .env file
        $envContent = @"
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/mediaboard_ai

# Security
SECRET_KEY=your-super-secret-key-here-generate-a-random-one
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Frontend
FRONTEND_ORIGIN=http://localhost:3000

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=100000000

# Redis (for caching and real-time features)
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "📋 Created .env file with template" -ForegroundColor Green
    }
    Write-Host "⚠️  Please update the .env file with your actual configuration values!" -ForegroundColor Yellow
}

# Create necessary directories
$directories = @("uploads", "logs", "data")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "📁 Created directory: $dir" -ForegroundColor Green
    }
}

# Database setup prompt
Write-Host "`n🗄️  Database Setup" -ForegroundColor Cyan
Write-Host "-" * 20 -ForegroundColor Cyan
Write-Host "Make sure PostgreSQL is installed and running." -ForegroundColor Yellow
Write-Host "Create a database named 'mediaboard_ai' or update DATABASE_URL in .env" -ForegroundColor Yellow

$dbChoice = Read-Host "Do you want to run database migrations now? (y/n)"
if ($dbChoice -eq "y") {
    Write-Host "🔄 Running database migrations..." -ForegroundColor Yellow
    alembic upgrade head
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migrations completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Migration failed. Make sure PostgreSQL is running and DATABASE_URL is correct." -ForegroundColor Red
    }
}

# Configuration check
Write-Host "`n🔧 Configuration Check" -ForegroundColor Cyan
Write-Host "-" * 25 -ForegroundColor Cyan
Write-Host "Please ensure the following are configured:" -ForegroundColor White
Write-Host "1. PostgreSQL database is running" -ForegroundColor Yellow
Write-Host "2. Google OAuth credentials are set in .env" -ForegroundColor Yellow
Write-Host "3. OpenAI API key is set (for AI features)" -ForegroundColor Yellow
Write-Host "4. Update SECRET_KEY in .env with a secure random string" -ForegroundColor Yellow

# Start server prompt
Write-Host "`n🚀 Starting Application" -ForegroundColor Cyan
Write-Host "-" * 25 -ForegroundColor Cyan

$startChoice = Read-Host "Ready to start the server? (y/n)"
if ($startChoice -eq "y") {
    Write-Host "🚀 Starting MediaBoard AI server..." -ForegroundColor Green
    Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API docs will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} else {
    Write-Host "`n👋 Setup completed!" -ForegroundColor Green
    Write-Host "To start the server manually:" -ForegroundColor White
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "  uvicorn app.main:app --reload" -ForegroundColor Cyan
}

Write-Host "`nFor more information, check the README.md file!" -ForegroundColor Green

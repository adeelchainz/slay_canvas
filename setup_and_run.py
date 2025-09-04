#!/usr/bin/env python3
"""
Slay Canvas - Startup Script
This script helps set up and run the Slay Canvas application
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path
import importlib.util

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def setup_environment():
    """Set up environment variables"""
    print("🔧 Setting up environment...")
    
    env_example_path = Path(".env.example")
    env_path = Path(".env")
    
    if not env_path.exists() and env_example_path.exists():
        # Copy .env.example to .env
        with open(env_example_path, 'r') as src, open(env_path, 'w') as dst:
            dst.write(src.read())
        print("📋 Created .env file from .env.example")
        print("⚠️  Please update the .env file with your actual configuration values!")
    
    # Check for required environment variables
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the required values.")

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "uploads",
        "logs",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created!")

async def init_database():
    """Initialize the database"""
    print("🗄️  Initializing database...")
    
    try:
        from app.db.session import init_db
        await init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        print("Make sure PostgreSQL is running and the DATABASE_URL is correct.")

def run_migrations():
    """Run Alembic migrations"""
    print("🔄 Running database migrations...")
    
    try:
        subprocess.check_call(["alembic", "upgrade", "head"])
        print("✅ Migrations completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run migrations: {e}")
        print("You may need to initialize Alembic first:")
        print("  alembic init alembic")
        print("  alembic revision --autogenerate -m 'Initial migration'")

async def init_database():
    """Initialize database tables"""
    try:
        # Import database initialization
        sys.path.append(os.getcwd())
        from app.db.init_db import init_database
        
        await init_database()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

async def check_database():
    """Check database connection"""
    try:
        sys.path.append(os.getcwd())
        from app.db.init_db import check_database_connection
        
        return await check_database_connection()
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Slay Canvas server...")
    
    try:
        cmd = [
            "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ]
        # Activate virtual environment if it exists
        venv_python = Path(".venv/Scripts/python.exe")
        if venv_python.exists():
            cmd[0] = str(venv_python)
            cmd.insert(1, "-m")
            cmd.insert(2, "uvicorn")
            
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def setup_database():
    """Helper to set up database with sample data"""
    print("\n🐘 PostgreSQL Setup Guide")
    print("-" * 30)
    print("1. Install PostgreSQL:")
    print("   - Download from: https://www.postgresql.org/download/")
    print("   - Or use Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres")
    print("\n2. Create database:")
    print("   - Database name: mediaboard_ai")
    print("   - Username: your_username") 
    print("   - Password: your_password")
    print("\n3. Update your .env file:")
    print("   DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/mediaboard_ai")
    print("\n4. Run migrations after database is ready")
    return input("\nHave you set up PostgreSQL? (y/n): ").lower() == 'y'

def main():
    """Main setup and run function"""
    print("🎨 Slay Canvas - Setup & Run")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Setup steps
    setup_environment()
    create_directories()
    install_dependencies()
    
    # Database setup
    print("\n🗄️  Database Setup")
    print("-" * 20)
    
    db_ready = setup_database()
    
    if db_ready:
        choice = input("Do you want to initialize the database? (y/n): ").lower()
        if choice == 'y':
            asyncio.run(init_database())
        
        choice = input("Do you want to run migrations? (y/n): ").lower()
        if choice == 'y':
            run_migrations()
    else:
        print("⚠️  Skipping database setup. You can run migrations later.")
    
    print("\n🔧 Configuration Check")
    print("-" * 25)
    print("Please ensure the following are configured:")
    print("1. PostgreSQL database is running")
    print("2. Google OAuth credentials are set in .env")
    print("3. OpenAI API key is set (for AI features)")
    print("4. Upload directory permissions are correct")
    
    print("\n🚀 Starting Application")
    print("-" * 25)
    
    choice = input("Ready to start the server? (y/n): ").lower()
    if choice == 'y':
        start_server()
    else:
        print("👋 Setup completed. Run 'uvicorn app.main:app --reload' to start the server manually.")

if __name__ == "__main__":
    main()

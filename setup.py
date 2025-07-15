#!/usr/bin/env python3
"""
Setup script for AI Job Application Auto-Filler
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 Setting up AI Job Application Auto-Filler...")
    
    # Check if Python is available
    if not run_command("python --version", "Checking Python installation"):
        print("❌ Python is not installed or not in PATH")
        return False
    
    # Install backend dependencies
    print("\n📦 Installing backend dependencies...")
    if not run_command("cd backend && pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Install Playwright browsers
    print("\n🌐 Installing Playwright browsers...")
    if not run_command("cd backend && playwright install chromium", "Installing Playwright browsers"):
        return False
    
    # Install frontend dependencies
    print("\n📦 Installing frontend dependencies...")
    if not run_command("cd frontend && npm install", "Installing Node.js dependencies"):
        return False
    
    # Create .env file if it doesn't exist
    backend_env_path = "backend/.env"
    if not os.path.exists(backend_env_path):
        print("\n📝 Creating environment file...")
        with open(backend_env_path, "w") as f:
            f.write("# Copy from env.example and add your API keys\n")
            f.write("OPENAI_API_KEY=\n")
            f.write("HUGGINGFACE_API_KEY=\n")
        print("✅ Created backend/.env file")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Add your API keys to backend/.env (optional)")
    print("2. Start the backend: cd backend && python main.py")
    print("3. Start the frontend: cd frontend && npm start")
    print("4. Open http://localhost:3000 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
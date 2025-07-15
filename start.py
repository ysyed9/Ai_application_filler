#!/usr/bin/env python3
"""
Startup script for AI Job Application Auto-Filler
"""

import subprocess
import sys
import os
import time
import threading
import signal
import requests

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        import playwright
        print("✅ Python dependencies found")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Run: cd backend && pip install -r requirements.txt")
        return False
    
    # Check if Playwright browsers are installed
    try:
        result = subprocess.run(
            ["playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True
        )
        if "chromium" not in result.stdout:
            print("❌ Playwright browsers not installed")
            print("Run: playwright install chromium")
            return False
        print("✅ Playwright browsers found")
    except FileNotFoundError:
        print("❌ Playwright not found")
        print("Run: playwright install chromium")
        return False
    
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    try:
        subprocess.run(
            ["python", "main.py"],
            cwd="backend",
            check=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend server failed: {e}")
        return False
    return True

def start_frontend():
    """Start the React frontend server"""
    print("🚀 Starting frontend server...")
    try:
        subprocess.run(
            ["npm", "start"],
            cwd="frontend",
            check=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend server failed: {e}")
        return False
    return True

def wait_for_backend():
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to start...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000/", timeout=1)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    
    print("❌ Backend failed to start")
    return False

def main():
    print("🎯 AI Job Application Auto-Filler")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait for backend to be ready
    if not wait_for_backend():
        return False
    
    # Start frontend
    print("\n🌐 Starting frontend...")
    return start_frontend()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0) 
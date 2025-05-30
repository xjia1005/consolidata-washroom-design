#!/usr/bin/env python3
"""
Consolidata Washroom Design - Startup Script
Starts both the API server and HTTP server for the complete system
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = ['flask', 'flask_cors']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please install manually:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    
    return True

def start_api_server():
    """Start the Flask API server"""
    print("🚀 Starting API server...")
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run([sys.executable, 'backend/app.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ API server failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 API server stopped")

def start_http_server():
    """Start the HTTP server for frontend"""
    print("🌐 Starting HTTP server...")
    try:
        # Wait a moment for API server to start
        time.sleep(2)
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run([sys.executable, '-m', 'http.server', '8000'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ HTTP server failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 HTTP server stopped")

def main():
    """Main startup function"""
    print("🏗️ Consolidata Washroom Design System")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create database directory if it doesn't exist
    db_dir = Path("database")
    db_dir.mkdir(exist_ok=True)
    
    print("✅ System ready to start")
    print("\n📋 Starting servers...")
    print("   - API Server: http://localhost:5000")
    print("   - Frontend: http://localhost:8000")
    print("\n🌐 Access the application at: http://localhost:8000/frontend/index.html")
    print("\n⚠️  Press Ctrl+C to stop both servers")
    
    try:
        # Start API server in a separate thread
        api_thread = threading.Thread(target=start_api_server, daemon=True)
        api_thread.start()
        
        # Start HTTP server in main thread
        start_http_server()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        print("✅ Consolidata system stopped")

if __name__ == '__main__':
    main() 
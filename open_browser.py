#!/usr/bin/env python3
"""
Browser Launcher for Consolidata Washroom Design System
Opens the web interface in your default browser
"""

import webbrowser
import time
import requests
import sys

def check_server_running(url="http://localhost:5000"):
    """Check if the server is running"""
    try:
        response = requests.get(f"{url}/api/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def main():
    print("🌐 Consolidata Washroom Design System - Browser Launcher")
    print("=" * 60)
    
    # Check if server is running
    if check_server_running():
        print("✅ Server is running at http://localhost:5000")
        
        # Open browser to frontend
        frontend_url = "http://localhost:5000/frontend/index.html"
        print(f"🚀 Opening browser to: {frontend_url}")
        
        try:
            webbrowser.open(frontend_url)
            print("✅ Browser opened successfully!")
            print("\n📋 Manual Testing Guide:")
            print("- Follow the steps in 'manual_user_testing_guide.md'")
            print("- Test all 6 scenarios step by step")
            print("- Verify all 3 critical functions work")
            print("- Check for any red flags or issues")
            
        except Exception as e:
            print(f"❌ Error opening browser: {e}")
            print(f"Please manually open: {frontend_url}")
            
    else:
        print("❌ Server is not running!")
        print("Please start the server first:")
        print("  python start.py")
        print("\nThen run this script again:")
        print("  python open_browser.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 
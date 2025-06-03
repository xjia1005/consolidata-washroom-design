#!/usr/bin/env python3
"""
WSGI Entry Point for Production Deployment
"""

import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import app

# Set production environment
os.environ['FLASK_ENV'] = 'production'

if __name__ == "__main__":
    app.run() 
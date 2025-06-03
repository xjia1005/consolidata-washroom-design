#!/usr/bin/env python3
"""
Production-ready Consolidata Washroom Design API
Optimized for deployment with proper error handling and logging
"""

import os
import logging
from flask import Flask
from backend.app import app, api

# Configure production logging
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    
    # Disable debug mode
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Security headers
    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 
#!/usr/bin/env python3
"""
BCode Pro - User Authentication and Subscription System
Handles user registration, login, subscription management, and payment processing
"""

import sqlite3
import hashlib
import secrets
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
import stripe
import os
from flask import session, request, jsonify
import re

class UserAuthSystem:
    def __init__(self, db_path="database/users.db"):
        self.db_path = db_path
        self.init_user_database()
        
        # Stripe configuration (you'll need to set these environment variables)
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        self.stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        
    def init_user_database(self):
        """Initialize user database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                company TEXT,
                profession TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token TEXT,
                reset_token TEXT,
                reset_token_expires TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_type TEXT NOT NULL,
                status TEXT NOT NULL,
                stripe_subscription_id TEXT,
                stripe_customer_id TEXT,
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Project usage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                project_name TEXT,
                analysis_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_free_tier BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Payment history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stripe_payment_intent_id TEXT,
                amount INTEGER,
                currency TEXT DEFAULT 'usd',
                status TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        try:
            salt, hash_hex = password_hash.split(':')
            password_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_check.hex() == hash_hex
        except:
            return False
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone):
        """Validate phone number format"""
        if not phone:
            return True  # Phone is optional
        pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
        return re.match(pattern, phone) is not None
    
    def register_user(self, email, password, first_name, last_name, phone=None, company=None, profession=None):
        """Register a new user"""
        try:
            # Validation
            if not self.validate_email(email):
                return {'success': False, 'error': 'Invalid email format'}
            
            if not self.validate_phone(phone):
                return {'success': False, 'error': 'Invalid phone number format'}
            
            if len(password) < 8:
                return {'success': False, 'error': 'Password must be at least 8 characters'}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return {'success': False, 'error': 'Email already registered'}
            
            # Create user
            password_hash = self.hash_password(password)
            verification_token = secrets.token_urlsafe(32)
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, phone, 
                                 company, profession, verification_token)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, first_name, last_name, phone, company, profession, verification_token))
            
            user_id = cursor.lastrowid
            
            # Create free tier subscription
            cursor.execute('''
                INSERT INTO subscriptions (user_id, plan_type, status)
                VALUES (?, 'free', 'active')
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            # Send verification email
            self.send_verification_email(email, verification_token)
            
            return {
                'success': True, 
                'message': 'Registration successful! Please check your email to verify your account.',
                'user_id': user_id
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Registration failed: {str(e)}'}
    
    def login_user(self, email, password):
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, password_hash, email_verified, is_active, first_name, last_name
                FROM users WHERE email = ?
            ''', (email,))
            
            user = cursor.fetchone()
            if not user:
                return {'success': False, 'error': 'Invalid email or password'}
            
            user_id, password_hash, email_verified, is_active, first_name, last_name = user
            
            if not self.verify_password(password, password_hash):
                return {'success': False, 'error': 'Invalid email or password'}
            
            if not is_active:
                return {'success': False, 'error': 'Account is deactivated'}
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'user_id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'email_verified': email_verified
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Login failed: {str(e)}'}
    
    def get_user_subscription(self, user_id):
        """Get user's current subscription details"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT plan_type, status, current_period_end, stripe_subscription_id
                FROM subscriptions WHERE user_id = ? AND status = 'active'
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id,))
            
            subscription = cursor.fetchone()
            if not subscription:
                return {'plan_type': 'none', 'status': 'inactive'}
            
            plan_type, status, period_end, stripe_id = subscription
            
            # Get project usage for free tier
            if plan_type == 'free':
                cursor.execute('''
                    SELECT COUNT(*) FROM project_usage 
                    WHERE user_id = ? AND is_free_tier = TRUE
                ''', (user_id,))
                projects_used = cursor.fetchone()[0]
            else:
                projects_used = 0
            
            conn.close()
            
            return {
                'plan_type': plan_type,
                'status': status,
                'period_end': period_end,
                'projects_used': projects_used,
                'free_projects_remaining': max(0, 3 - projects_used) if plan_type == 'free' else 0
            }
            
        except Exception as e:
            return {'plan_type': 'none', 'status': 'error', 'error': str(e)}
    
    def can_use_service(self, user_id, analysis_type='standard'):
        """Check if user can use the service based on their subscription"""
        subscription = self.get_user_subscription(user_id)
        
        if subscription['plan_type'] == 'free':
            return subscription['free_projects_remaining'] > 0
        elif subscription['plan_type'] in ['professional', 'project', 'team', 'enterprise']:
            return subscription['status'] == 'active'
        else:
            return False
    
    def record_project_usage(self, user_id, project_name, analysis_type):
        """Record project usage for billing/limits"""
        try:
            subscription = self.get_user_subscription(user_id)
            is_free_tier = subscription['plan_type'] == 'free'
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO project_usage (user_id, project_name, analysis_type, is_free_tier)
                VALUES (?, ?, ?, ?)
            ''', (user_id, project_name, analysis_type, is_free_tier))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_stripe_checkout_session(self, user_id, plan_type):
        """Create Stripe checkout session for subscription"""
        try:
            # Plan pricing
            prices = {
                'professional': 'price_professional_monthly',  # You'll create these in Stripe
                'project': 'price_project_single',
                'team': 'price_team_monthly',
                'enterprise': 'price_enterprise_monthly'
            }
            
            if plan_type not in prices:
                return {'success': False, 'error': 'Invalid plan type'}
            
            # Get user email
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
            user_email = cursor.fetchone()[0]
            conn.close()
            
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                customer_email=user_email,
                payment_method_types=['card'],
                line_items=[{
                    'price': prices[plan_type],
                    'quantity': 1,
                }],
                mode='subscription' if plan_type != 'project' else 'payment',
                success_url=f'https://bcodepro.com/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url='https://bcodepro.com/pricing',
                metadata={
                    'user_id': user_id,
                    'plan_type': plan_type
                }
            )
            
            return {
                'success': True,
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_verification_email(self, email, token):
        """Send email verification"""
        try:
            # Configure your SMTP settings
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            smtp_username = os.environ.get('SMTP_USERNAME')
            smtp_password = os.environ.get('SMTP_PASSWORD')
            
            if not all([smtp_username, smtp_password]):
                print("SMTP credentials not configured")
                return False
            
            msg = MimeMultipart()
            msg['From'] = smtp_username
            msg['To'] = email
            msg['Subject'] = "Verify your BCode Pro account"
            
            body = f"""
            Welcome to BCode Pro!
            
            Please verify your email address by clicking the link below:
            https://bcodepro.com/verify-email?token={token}
            
            This link will expire in 24 hours.
            
            Best regards,
            The BCode Pro Team
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False

# Pricing configuration
PRICING_PLANS = {
    'free': {
        'name': 'Free Trial',
        'price': 0,
        'projects': 3,
        'billing': 'free',
        'features': [
            '3 free projects',
            'Basic analysis',
            'Building code compliance',
            'Watermarked exports',
            'Email support'
        ],
        'limitations': [
            'Watermarked exports',
            'Basic analysis only',
            'No CAD exports'
        ]
    },
    'professional': {
        'name': 'Individual Professional',
        'price': 29,
        'annual_price': 290,  # Save 2 months
        'billing': 'monthly',
        'popular': True,
        'features': [
            'Unlimited projects',
            'Enhanced 7-step analysis',
            'Professional exports (no watermarks)',
            'CAD file exports (DXF/DWG)',
            'PDF compliance reports',
            'All building codes (NBC, Alberta, Ontario, BC)',
            'Priority email support',
            'Compliance guarantee*'
        ],
        'target': 'Solo architects, junior designers, consultants'
    },
    'project': {
        'name': 'Pay Per Project',
        'price': 15,
        'billing': 'per project',
        'features': [
            'Single project access',
            'All professional features',
            '30-day project access',
            'Professional exports',
            'CAD file exports',
            'Priority support',
            'No monthly commitment',
            'Perfect for occasional use'
        ],
        'target': 'Consultants, occasional users'
    },
    'firm': {
        'name': 'Small/Medium Firm',
        'price': 149,
        'annual_price': 1490,  # Save 2 months
        'billing': 'monthly',
        'users': '10 users',
        'new': True,
        'features': [
            'Everything in Professional',
            'Up to 10 team members',
            'Team collaboration & sharing',
            'Custom branding on reports',
            'Bulk project management',
            'Usage analytics & reporting',
            'Phone + email support',
            'Compliance guarantee*',
            '5 bonus credits/month for add-ons'
        ],
        'target': 'Small/medium architecture studios, MEP firms'
    },
    'team': {
        'name': 'Large Team',
        'price': 99,
        'annual_price': 990,  # Save 2 months
        'billing': 'monthly',
        'users': '5 users',
        'features': [
            'Everything in Professional',
            'Up to 5 team members',
            'Team collaboration',
            'Custom branding on reports',
            'API access (basic)',
            'Priority support',
            'Usage analytics',
            'Compliance guarantee*'
        ],
        'target': 'Boutique studios, specialized consultants'
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 299,
        'annual_price': 2990,  # Save 2 months
        'billing': 'monthly',
        'users': 'Unlimited users',
        'features': [
            'Everything in Firm plan',
            'Unlimited users',
            'Custom jurisdictions & codes',
            'White-label options',
            'Dedicated account manager',
            'Custom integrations & API',
            'SLA guarantee (99.9% uptime)',
            'Compliance guarantee*',
            'Unlimited credits for add-ons',
            'Custom training & onboarding'
        ],
        'target': 'Large multidisciplinary firms, public sector'
    }
}

# Add-on credits system
ADDON_CREDITS = {
    'extra_jurisdiction': {
        'name': 'Additional Jurisdiction',
        'price': 5,
        'credits': 1,
        'description': 'Add support for additional building codes (IBC, local codes)'
    },
    '3d_layout_export': {
        'name': '3D Layout Export',
        'price': 10,
        'credits': 2,
        'description': 'Export 3D models for Revit/SketchUp integration'
    },
    'expedited_review': {
        'name': 'Expedited Compliance Review',
        'price': 25,
        'credits': 5,
        'description': 'Human expert review within 24 hours'
    },
    'custom_template': {
        'name': 'Custom Report Template',
        'price': 15,
        'credits': 3,
        'description': 'Branded report templates with your firm logo'
    },
    'bim_integration': {
        'name': 'BIM Integration Setup',
        'price': 50,
        'credits': 10,
        'description': 'Custom AutoCAD/Revit plugin configuration'
    }
}

# Compliance guarantee terms
COMPLIANCE_GUARANTEE = """
*Compliance Guarantee: Our analysis includes specific building code clause references. 
If any regulatory authority disputes our compliance recommendations and you can demonstrate 
the error was in our analysis (not project-specific conditions), we will:
1. Work with you to resolve the issue at no charge
2. Provide expert consultation to address the concern
3. Offer a full refund if we cannot resolve the dispute
This guarantee applies to standard building code interpretations within supported jurisdictions.
""" 
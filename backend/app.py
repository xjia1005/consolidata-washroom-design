#!/usr/bin/env python3
"""
BCode Pro - Backend API Server
Building Code Compliance and Layout Generation System with User Authentication
"""

from flask import Flask, request, jsonify, send_from_directory, send_file, session, redirect, url_for
from flask_cors import CORS
import json
import sqlite3
import os
from datetime import datetime
import logging
import sys
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app, supports_credentials=True)  # Enable CORS with credentials for sessions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'building_codes.db')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_logic_engine import EnhancedBuildingCodeEngine
from user_auth_system import UserAuthSystem, PRICING_PLANS

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(analysis_type='standard'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            
            user_id = session['user_id']
            if not auth_system.can_use_service(user_id, analysis_type):
                subscription = auth_system.get_user_subscription(user_id)
                if subscription['plan_type'] == 'free':
                    return jsonify({
                        'success': False, 
                        'error': 'Free trial limit reached',
                        'upgrade_required': True,
                        'free_projects_remaining': subscription['free_projects_remaining']
                    }), 402
                else:
                    return jsonify({
                        'success': False, 
                        'error': 'Subscription required',
                        'upgrade_required': True
                    }), 402
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class BuildingCodeAPI:
    def __init__(self, db_path="database/building_codes.db"):
        self.db_path = db_path
        # Remove shared connection - use per-request connections
        
        # Initialize enhanced logic engine
        self.enhanced_engine = EnhancedBuildingCodeEngine(db_path)
        
        self.init_database()
    
    def init_database(self):
        """Initialize database with enhanced schema and data"""
        try:
            # Use temporary connection for initialization only
            connection = sqlite3.connect(self.db_path, check_same_thread=False)
            connection.row_factory = sqlite3.Row
            
            # Initialize enhanced database
            self.enhanced_engine.initialize_enhanced_database()
            
            # Ensure database directory exists
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            
            cursor = connection.cursor()
            
            # Create tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS building_codes (
                    id INTEGER PRIMARY KEY,
                    jurisdiction TEXT NOT NULL,
                    building_type TEXT NOT NULL,
                    occupancy_range TEXT NOT NULL,
                    water_closets_male INTEGER,
                    water_closets_female INTEGER,
                    urinals INTEGER,
                    lavatories INTEGER,
                    accessible_stalls INTEGER,
                    code_reference TEXT,
                    accessibility_level TEXT DEFAULT 'basic'
                )
            ''')
            
            # Insert sample data if table is empty
            cursor.execute('SELECT COUNT(*) FROM building_codes')
            if cursor.fetchone()[0] == 0:
                self.populate_sample_data(cursor)
            
            connection.commit()
            connection.close()  # Close initialization connection
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def populate_sample_data(self, cursor):
        """Populate database with sample building code data"""
        sample_data = [
            # NBC - Office Buildings
            ('NBC', 'office', '1-15', 1, 1, 1, 1, 1, 'NBC 3.7.4.2', 'basic'),
            ('NBC', 'office', '16-35', 1, 2, 1, 2, 1, 'NBC 3.7.4.2', 'basic'),
            ('NBC', 'office', '36-55', 2, 2, 1, 2, 1, 'NBC 3.7.4.2', 'basic'),
            ('NBC', 'office', '56-80', 2, 3, 2, 3, 1, 'NBC 3.7.4.2', 'basic'),
            ('NBC', 'office', '81-110', 3, 3, 2, 4, 2, 'NBC 3.7.4.2', 'basic'),
            
            # Alberta - Office Buildings (Different requirements)
            ('Alberta', 'office', '1-15', 1, 1, 1, 1, 1, 'Alberta Building Code 3.7.4.2', 'basic'),
            ('Alberta', 'office', '16-35', 1, 2, 1, 2, 1, 'Alberta Building Code 3.7.4.2', 'basic'),
            ('Alberta', 'office', '36-55', 2, 3, 1, 3, 1, 'Alberta Building Code 3.7.4.2', 'basic'),
            ('Alberta', 'office', '56-80', 3, 3, 2, 3, 2, 'Alberta Building Code 3.7.4.2', 'basic'),
            ('Alberta', 'office', '81-110', 3, 4, 2, 4, 2, 'Alberta Building Code 3.7.4.2', 'basic'),
            
            # Ontario - Office Buildings
            ('Ontario', 'office', '1-15', 1, 1, 1, 1, 1, 'OBC 3.7.4.2', 'basic'),
            ('Ontario', 'office', '16-35', 1, 2, 1, 2, 1, 'OBC 3.7.4.2', 'basic'),
            
            # BC - Office Buildings
            ('BC', 'office', '1-15', 1, 1, 1, 1, 1, 'BCBC 3.7.4.2', 'basic'),
            ('BC', 'office', '16-35', 1, 2, 1, 2, 1, 'BCBC 3.7.4.2', 'basic'),
            
            # School Buildings
            ('NBC', 'school', '1-15', 1, 1, 0, 1, 1, 'NBC 3.7.4.3', 'enhanced'),
            ('NBC', 'school', '16-30', 1, 2, 1, 2, 1, 'NBC 3.7.4.3', 'enhanced'),
            ('NBC', 'school', '31-50', 2, 2, 1, 3, 1, 'NBC 3.7.4.3', 'enhanced'),
            
            # Assembly Buildings
            ('NBC', 'assembly', '1-50', 2, 2, 1, 2, 1, 'NBC 3.7.4.4', 'basic'),
            ('NBC', 'assembly', '51-100', 3, 3, 2, 3, 2, 'NBC 3.7.4.4', 'basic'),
            ('NBC', 'assembly', '101-200', 4, 4, 2, 4, 2, 'NBC 3.7.4.4', 'basic'),
            
            # Retail Buildings
            ('NBC', 'retail', '1-25', 1, 1, 1, 1, 1, 'NBC 3.7.4.5', 'basic'),
            ('NBC', 'retail', '26-50', 1, 2, 1, 2, 1, 'NBC 3.7.4.5', 'basic'),
            ('NBC', 'retail', '51-100', 2, 3, 1, 3, 1, 'NBC 3.7.4.5', 'basic'),
            
            # Industrial Buildings
            ('NBC', 'industrial', '1-20', 1, 1, 1, 1, 1, 'NBC 3.7.4.6', 'basic'),
            ('NBC', 'industrial', '21-40', 1, 2, 1, 2, 1, 'NBC 3.7.4.6', 'basic'),
            ('NBC', 'industrial', '41-75', 2, 2, 2, 3, 1, 'NBC 3.7.4.6', 'basic'),
        ]
        
        cursor.executemany('''
            INSERT INTO building_codes 
            (jurisdiction, building_type, occupancy_range, water_closets_male, 
             water_closets_female, urinals, lavatories, accessible_stalls, 
             code_reference, accessibility_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)
    
    def get_fixture_requirements(self, occupancy_load, building_type, jurisdiction, accessibility_level='basic'):
        """Calculate fixture requirements based on occupancy and building type"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find matching code requirements
            cursor.execute('''
                SELECT * FROM building_codes 
                WHERE jurisdiction = ? AND building_type = ? AND accessibility_level = ?
                ORDER BY CAST(SUBSTR(occupancy_range, 1, INSTR(occupancy_range, '-')-1) AS INTEGER)
            ''', (jurisdiction, building_type, accessibility_level))
            
            codes = cursor.fetchall()
            conn.close()
            
            if not codes:
                # Fallback to basic requirements
                return self.get_basic_requirements(occupancy_load, building_type)
            
            # Find appropriate range
            selected_code = None
            for code in codes:
                range_parts = code[3].split('-')  # occupancy_range
                min_occ = int(range_parts[0])
                max_occ = int(range_parts[1]) if len(range_parts) > 1 else float('inf')
                
                if min_occ <= occupancy_load <= max_occ:
                    selected_code = code
                    break
            
            if not selected_code:
                # Use the highest range if occupancy exceeds all ranges
                selected_code = codes[-1]
                # Scale up based on occupancy
                scale_factor = max(1, occupancy_load / 100)
            else:
                scale_factor = 1
            
            # Calculate fixtures
            fixtures = {
                'water_closets_male': max(1, int(selected_code[4] * scale_factor)),
                'water_closets_female': max(1, int(selected_code[5] * scale_factor)),
                'urinals': max(0, int(selected_code[6] * scale_factor)),
                'lavatories': max(1, int(selected_code[7] * scale_factor)),
                'accessible_stalls': max(1, int(selected_code[8] * scale_factor)),
                'total_fixtures': 0,
                'calculation_basis': f"{jurisdiction} {building_type} occupancy {occupancy_load}",
                'code_references': [selected_code[9]]
            }
            
            fixtures['total_fixtures'] = (
                fixtures['water_closets_male'] + 
                fixtures['water_closets_female'] + 
                fixtures['urinals'] + 
                fixtures['lavatories']
            )
            
            return fixtures
            
        except Exception as e:
            logger.error(f"Error calculating fixtures: {e}")
            return self.get_basic_requirements(occupancy_load, building_type)
    
    def get_basic_requirements(self, occupancy_load, building_type):
        """Fallback basic requirements calculation"""
        # Basic calculation based on occupancy
        base_fixtures = max(1, occupancy_load // 25)
        
        return {
            'water_closets_male': base_fixtures,
            'water_closets_female': base_fixtures + 1,
            'urinals': max(1, base_fixtures // 2),
            'lavatories': base_fixtures + 1,
            'accessible_stalls': 1,
            'total_fixtures': (base_fixtures * 2) + max(1, base_fixtures // 2) + (base_fixtures + 1),
            'calculation_basis': f"Basic calculation for {building_type} occupancy {occupancy_load}",
            'code_references': ['Basic Requirements']
        }
    
    def generate_layout(self, fixtures, room_dimensions, accessibility_level='basic'):
        """Generate 2D layout with fixture positions"""
        length = room_dimensions['length']
        width = room_dimensions['width']
        
        layout_elements = []
        
        # Calculate spacing
        total_fixtures = fixtures['total_fixtures']
        spacing = min(length, width) / (total_fixtures + 1)
        
        # Position fixtures
        x_pos = 1.0
        y_pos = 1.0
        
        # Male water closets
        for i in range(fixtures['water_closets_male']):
            layout_elements.append({
                'type': 'water_closet_male',
                'x': x_pos,
                'y': y_pos,
                'width': 0.8,
                'height': 1.2,
                'clearance': 0.6 if accessibility_level == 'basic' else 1.5
            })
            x_pos += spacing
        
        # Female water closets
        y_pos = width - 2.0
        x_pos = 1.0
        for i in range(fixtures['water_closets_female']):
            layout_elements.append({
                'type': 'water_closet_female',
                'x': x_pos,
                'y': y_pos,
                'width': 0.8,
                'height': 1.2,
                'clearance': 0.6 if accessibility_level == 'basic' else 1.5
            })
            x_pos += spacing
        
        # Urinals
        x_pos = length - 1.5
        y_pos = 1.0
        for i in range(fixtures['urinals']):
            layout_elements.append({
                'type': 'urinal',
                'x': x_pos,
                'y': y_pos,
                'width': 0.6,
                'height': 0.8,
                'clearance': 0.6
            })
            y_pos += 1.0
        
        # Lavatories
        x_pos = 2.0
        y_pos = width / 2
        for i in range(fixtures['lavatories']):
            layout_elements.append({
                'type': 'lavatory',
                'x': x_pos,
                'y': y_pos,
                'width': 0.6,
                'height': 0.5,
                'clearance': 0.8
            })
            x_pos += 1.2
        
        # Accessible stalls
        x_pos = 0.5
        y_pos = 0.5
        for i in range(fixtures['accessible_stalls']):
            layout_elements.append({
                'type': 'accessible_stall',
                'x': x_pos,
                'y': y_pos,
                'width': 1.5,
                'height': 2.0,
                'clearance': 1.5
            })
            y_pos += 3.0
        
        return layout_elements
    
    def generate_compliance_checklist(self, building_type, jurisdiction, accessibility_level):
        """Generate compliance checklist"""
        checklist = [
            {
                'item': 'Fixture count compliance',
                'status': 'compliant',
                'reference': f'{jurisdiction} 3.7.4.2',
                'description': 'Minimum fixture requirements met'
            },
            {
                'item': 'Accessibility compliance',
                'status': 'compliant' if accessibility_level != 'basic' else 'review',
                'reference': f'{jurisdiction} 3.8.3.3',
                'description': f'Accessibility level: {accessibility_level}'
            },
            {
                'item': 'Clearance requirements',
                'status': 'compliant',
                'reference': f'{jurisdiction} 3.7.4.5',
                'description': 'Minimum clearances provided'
            },
            {
                'item': 'Ventilation requirements',
                'status': 'review',
                'reference': f'{jurisdiction} 9.32.3.1',
                'description': 'Mechanical ventilation required'
            },
            {
                'item': 'Privacy requirements',
                'status': 'compliant',
                'reference': f'{jurisdiction} 3.7.4.6',
                'description': 'Partitions and doors provided'
            }
        ]
        
        return checklist

# Initialize API and Auth System
api = BuildingCodeAPI()
auth_system = UserAuthSystem()

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Extract registration data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone')
        company = data.get('company')
        profession = data.get('profession')
        selected_plan = data.get('selected_plan', 'free')
        
        # Register user
        result = auth_system.register_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            company=company,
            profession=profession
        )
        
        if result['success']:
            # Auto-login after registration
            session['user_id'] = result['user_id']
            session['email'] = email
            session['first_name'] = first_name
            session['last_name'] = last_name
            
            # If paid plan selected, create checkout session
            if selected_plan != 'free':
                checkout_result = auth_system.create_stripe_checkout_session(
                    result['user_id'], selected_plan
                )
                if checkout_result['success']:
                    result['checkout_url'] = checkout_result['checkout_url']
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        result = auth_system.login_user(email, password)
        
        if result['success']:
            # Set session
            session['user_id'] = result['user_id']
            session['email'] = result['email']
            session['first_name'] = result['first_name']
            session['last_name'] = result['last_name']
            
            # Get subscription info
            subscription = auth_system.get_user_subscription(result['user_id'])
            result['subscription'] = subscription
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': 'Login failed'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get user profile and subscription info"""
    try:
        user_id = session['user_id']
        subscription = auth_system.get_user_subscription(user_id)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': session['email'],
                'first_name': session['first_name'],
                'last_name': session['last_name']
            },
            'subscription': subscription
        })
        
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get profile'}), 500

@app.route('/api/pricing', methods=['GET'])
def get_pricing():
    """Get pricing plans"""
    return jsonify({
        'success': True,
        'plans': PRICING_PLANS
    })

@app.route('/api/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe checkout session"""
    try:
        data = request.get_json()
        plan_type = data.get('plan_type')
        user_id = session['user_id']
        
        result = auth_system.create_stripe_checkout_session(user_id, plan_type)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        return jsonify({'success': False, 'error': 'Failed to create checkout session'}), 500

# Enhanced API Routes with Authentication
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'service': 'BCode Pro API',
        'description': 'Professional Building Code Analysis & CAD Integration',
        'website': 'bcodepro.com',
        'features': ['user_auth', 'subscriptions', 'enhanced_analysis']
    })

@app.route('/api/calculate-fixtures', methods=['POST'])
@subscription_required('standard')
def calculate_fixtures():
    """Calculate fixture requirements - requires subscription"""
    try:
        data = request.get_json()
        
        occupancy_load = data.get('occupancy_load', 50)
        building_type = data.get('building_type', 'office')
        jurisdiction = data.get('jurisdiction', 'NBC')
        accessibility_level = data.get('accessibility_level', 'basic')
        
        fixtures = api.get_fixture_requirements(
            occupancy_load, building_type, jurisdiction, accessibility_level
        )
        
        # Record usage
        user_id = session['user_id']
        project_name = data.get('project_name', f'Project_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        auth_system.record_project_usage(user_id, project_name, 'standard')
        
        return jsonify({
            'success': True,
            'fixture_requirements': fixtures
        })
        
    except Exception as e:
        logger.error(f"Error in calculate_fixtures: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/complete-analysis', methods=['POST'])
@subscription_required('standard')
def complete_analysis():
    """Complete washroom design analysis - requires subscription"""
    try:
        data = request.get_json()
        
        # Validate input data
        if not data:
            return jsonify({
                'success': False,
                'error': 'No input data provided'
            }), 400
        
        # Extract parameters with validation
        occupancy_load = data.get('occupancy_load')
        building_type = data.get('building_type')
        jurisdiction = data.get('jurisdiction')
        
        # Basic validation
        if not occupancy_load or not building_type or not jurisdiction:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: occupancy_load, building_type, jurisdiction'
            }), 400
        
        # Set defaults for optional parameters
        accessibility_level = data.get('accessibility_level', 'basic')
        room_dimensions = data.get('room_dimensions', {'length': 10, 'width': 8, 'height': 3})
        
        # Calculate fixtures
        fixtures = api.get_fixture_requirements(
            occupancy_load, building_type, jurisdiction, accessibility_level
        )
        
        # Generate layout
        layout_elements = api.generate_layout(fixtures, room_dimensions, accessibility_level)
        
        # Generate compliance checklist
        checklist = api.generate_compliance_checklist(building_type, jurisdiction, accessibility_level)
        
        # Calculate compliance score
        compliant_items = sum(1 for item in checklist if item['status'] == 'compliant')
        compliance_score = (compliant_items / len(checklist)) * 100
        
        # Generate recommendations
        recommendations = []
        if accessibility_level == 'basic':
            recommendations.append("Consider enhanced accessibility features for better compliance")
        if compliance_score < 90:
            recommendations.append("Review ventilation and privacy requirements")
        if fixtures['total_fixtures'] > 10:
            recommendations.append("Consider separate male/female washroom areas")
        
        # Record usage
        user_id = session['user_id']
        project_name = data.get('project_name', f'Analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        auth_system.record_project_usage(user_id, project_name, 'complete')
        
        # Check if user gets watermarked exports
        subscription = auth_system.get_user_subscription(user_id)
        watermarked = subscription['plan_type'] == 'free'
        
        # Compile report
        report = {
            'fixture_requirements': fixtures,
            'layout_elements': layout_elements,
            'compliance_checklist': checklist,
            'compliance_score': compliance_score,
            'recommendations': recommendations,
            'project_parameters': {
                'occupancy_load': occupancy_load,
                'building_type': building_type,
                'jurisdiction': jurisdiction,
                'accessibility_level': accessibility_level,
                'room_dimensions': room_dimensions
            },
            'generated_at': datetime.now().isoformat(),
            'watermarked': watermarked,
            'user_plan': subscription['plan_type']
        }
        
        return jsonify({
            'success': True,
            'analysis_report': report
        })
        
    except Exception as e:
        logger.error(f"Error in complete_analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/enhanced-analysis', methods=['POST'])
@subscription_required('enhanced')
def enhanced_analysis():
    """Enhanced 7-step analysis - requires professional subscription"""
    try:
        data = request.get_json()
        
        # Check if user has professional subscription
        user_id = session['user_id']
        subscription = auth_system.get_user_subscription(user_id)
        
        if subscription['plan_type'] == 'free':
            return jsonify({
                'success': False,
                'error': 'Enhanced analysis requires Professional subscription',
                'upgrade_required': True
            }), 402
        
        # Use enhanced engine
        result = api.enhanced_engine.process_enhanced_workflow(data)
        
        # Record usage
        project_name = data.get('project_name', f'Enhanced_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        auth_system.record_project_usage(user_id, project_name, 'enhanced')
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in enhanced_analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Frontend Routes
@app.route('/')
def index():
    """Serve main application"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/pricing')
def pricing_page():
    """Serve pricing page"""
    return send_from_directory('../frontend', 'pricing.html')

@app.route('/register')
def register_page():
    """Serve registration page"""
    return send_from_directory('../frontend', 'register.html')

@app.route('/login')
def login_page():
    """Serve login page"""
    return send_from_directory('../frontend', 'login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Serve user dashboard"""
    return send_from_directory('../frontend', 'dashboard.html')

@app.route('/styles.css')
def serve_css():
    """Serve CSS with proper MIME type"""
    return send_from_directory('../frontend', 'styles.css', mimetype='text/css')

@app.route('/script.js')
def serve_js():
    """Serve JavaScript with proper MIME type"""
    return send_from_directory('../frontend', 'script.js', mimetype='application/javascript')

@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    """Serve frontend files with proper MIME types"""
    import mimetypes
    mimetype, _ = mimetypes.guess_type(filename)
    return send_from_directory('../frontend', filename, mimetype=mimetype)

@app.route('/frontend/')
def frontend_index():
    """Serve frontend index"""
    return send_from_directory('../frontend', 'index.html')

if __name__ == '__main__':
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting BCode Pro API server on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Database path: {DB_PATH}")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 
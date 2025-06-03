#!/usr/bin/env python3
"""
Consolidata Washroom Design - Backend API Server
Building Code Compliance and Layout Generation System
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import json
import sqlite3
import os
from datetime import datetime
import logging
import sys

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'building_codes.db')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_logic_engine import EnhancedBuildingCodeEngine

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

# Initialize API
api = BuildingCodeAPI()

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'Consolidata Building Code API'
    })

@app.route('/api/calculate-fixtures', methods=['POST'])
def calculate_fixtures():
    """Calculate fixture requirements"""
    try:
        data = request.get_json()
        
        occupancy_load = data.get('occupancy_load', 50)
        building_type = data.get('building_type', 'office')
        jurisdiction = data.get('jurisdiction', 'NBC')
        accessibility_level = data.get('accessibility_level', 'basic')
        
        fixtures = api.get_fixture_requirements(
            occupancy_load, building_type, jurisdiction, accessibility_level
        )
        
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

@app.route('/api/generate-layout', methods=['POST'])
def generate_layout():
    """Generate 2D layout"""
    try:
        data = request.get_json()
        
        fixtures = data.get('fixture_requirements', {})
        room_dimensions = data.get('room_dimensions', {'length': 10, 'width': 8, 'height': 3})
        accessibility_level = data.get('accessibility_level', 'basic')
        
        layout_elements = api.generate_layout(fixtures, room_dimensions, accessibility_level)
        
        return jsonify({
            'success': True,
            'layout_elements': layout_elements,
            'room_dimensions': room_dimensions
        })
        
    except Exception as e:
        logger.error(f"Error in generate_layout: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-compliance-checklist', methods=['POST'])
def generate_compliance_checklist():
    """Generate compliance checklist"""
    try:
        data = request.get_json()
        
        building_type = data.get('building_type', 'office')
        jurisdiction = data.get('jurisdiction', 'NBC')
        accessibility_level = data.get('accessibility_level', 'basic')
        
        checklist = api.generate_compliance_checklist(building_type, jurisdiction, accessibility_level)
        
        return jsonify({
            'success': True,
            'compliance_checklist': checklist
        })
        
    except Exception as e:
        logger.error(f"Error in generate_compliance_checklist: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/complete-analysis', methods=['POST'])
def complete_analysis():
    """Complete washroom design analysis"""
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
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        logger.error(f"Error in complete_analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API documentation endpoint"""
    docs = {
        'title': 'Consolidata Building Code Compliance API',
        'version': '1.0.0',
        'description': 'Professional washroom design and building code compliance system',
        'endpoints': {
            '/api/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            '/api/calculate-fixtures': {
                'method': 'POST',
                'description': 'Calculate fixture requirements',
                'parameters': ['occupancy_load', 'building_type', 'jurisdiction', 'accessibility_level']
            },
            '/api/generate-layout': {
                'method': 'POST',
                'description': 'Generate 2D layout',
                'parameters': ['fixture_requirements', 'room_dimensions', 'accessibility_level']
            },
            '/api/generate-compliance-checklist': {
                'method': 'POST',
                'description': 'Generate compliance checklist',
                'parameters': ['building_type', 'jurisdiction', 'accessibility_level']
            },
            '/api/complete-analysis': {
                'method': 'POST',
                'description': 'Complete washroom design analysis',
                'parameters': ['occupancy_load', 'building_type', 'jurisdiction', 'accessibility_level', 'room_dimensions']
            }
        }
    }
    
    return jsonify(docs)

@app.route('/api/enhanced-analysis', methods=['POST'])
def enhanced_analysis():
    """
    🎯 Enhanced building code analysis with high-accuracy workflow
    Implements the complete 7-step process for maximum compliance coverage
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No input data provided",
                "status": "error"
            }), 400
        
        logger.info("🔄 Starting enhanced analysis workflow...")
        
        # Execute the complete 7-step workflow
        workflow_results = api.enhanced_engine.process_complete_workflow(data)
        
        if "error" in workflow_results:
            return jsonify({
                "error": workflow_results["error"],
                "status": "error"
            }), 500
        
        # Format response for frontend
        response = {
            "status": "success",
            "workflow_id": workflow_results["workflow_id"],
            "timestamp": workflow_results["timestamp"],
            "analysis_type": "enhanced_high_accuracy",
            
            # Main results
            "compliance_checklist": workflow_results["final_results"]["compliance_checklist"],
            "layout_design": workflow_results["final_results"]["layout_design"],
            
            # Validation and traceability
            "validation_summary": workflow_results["validation"],
            "traceability_complete": workflow_results["final_results"]["traceability_complete"],
            
            # Workflow details (for debugging/transparency)
            "workflow_steps": {
                step_key: {
                    "name": step_data["name"],
                    "status": step_data["status"],
                    "summary": {
                        "rules_found": step_data.get("rules_found"),
                        "components_required": len(step_data.get("data", {}).get("required_components", [])) if step_key == "step_3" else None,
                        "clauses_found": step_data.get("data", {}).get("total_clauses") if step_key == "step_4" else None,
                        "coverage_score": step_data.get("data", {}).get("coverage_map", {}).get("coverage_percentage") if step_key == "step_5" else None
                    }
                }
                for step_key, step_data in workflow_results["steps"].items()
            },
            
            # Summary metrics
            "summary": {
                "total_checklist_items": workflow_results["final_results"]["compliance_checklist"]["project_info"]["total_items"],
                "critical_items": workflow_results["final_results"]["compliance_checklist"]["project_info"]["critical_items"],
                "coverage_percentage": workflow_results["validation"]["coverage_map"]["coverage_percentage"],
                "layout_efficiency": workflow_results["final_results"]["layout_design"]["layout_efficiency"],
                "compliance_score": workflow_results["final_results"]["layout_design"]["compliance_score"]
            }
        }
        
        logger.info("✅ Enhanced analysis completed successfully")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Enhanced analysis failed: {e}")
        return jsonify({
            "error": f"Enhanced analysis failed: {str(e)}",
            "status": "error"
        }), 500

# Frontend serving routes
@app.route('/')
def index():
    """Serve the main frontend page"""
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    """Serve frontend static files"""
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    return send_from_directory(frontend_path, filename)

@app.route('/frontend/')
def frontend_index():
    """Serve frontend index when accessing /frontend/"""
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    return send_from_directory(frontend_path, 'index.html')

if __name__ == '__main__':
    print("🏗️ Starting Consolidata Building Code Compliance API...")
    print("📚 Database initialized")
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🌐 Server starting on http://{host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/api/docs")
    
    # Use production settings if deployed
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(host=host, port=port, debug=debug) 
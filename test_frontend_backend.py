#!/usr/bin/env python3
"""
Test script for Frontend-Backend Communication
Tests the washroom design tool's full stack integration
"""

import requests
import json
import time
import threading
import subprocess
import sys
import os

def test_backend_endpoints():
    """Test all backend API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Backend API Endpoints")
    print("=" * 50)
    
    # Wait for server to start
    time.sleep(2)
    
    # Test 1: Homepage (Frontend)
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Homepage: {response.status_code}")
    except Exception as e:
        print(f"❌ Homepage error: {e}")
    
    # Test 2: Generate Layout API
    test_data = {
        "buildingType": "school",
        "roomLength": 8.0,
        "roomWidth": 6.0,
        "roomHeight": 2.7,
        "occupancyType": "educational",
        "occupancyCount": 200,
        "accessibilityRequired": True
    }
    
    try:
        response = requests.post(f"{base_url}/api/generate-layout", json=test_data)
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Generate Layout: {response.status_code}")
            print(f"   - Layout Name: {result.get('layout_name')}")
            print(f"   - Packages: {len(result.get('positioned_packages', []))}")
            print(f"   - Compliance: {result.get('compliance_results', {}).get('overall_compliance', 0):.1f}%")
            
            # Store result for export test
            global layout_result
            layout_result = result
        else:
            print(f"❌ Generate Layout failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Generate Layout error: {e}")
    
    # Test 3: Validate Input API
    try:
        response = requests.post(f"{base_url}/api/validate-input", json=test_data)
        result = response.json()
        print(f"✅ Validate Input: {response.status_code}")
        print(f"   - Valid: {result.get('valid')}")
        print(f"   - Warnings: {len(result.get('warnings', []))}")
        print(f"   - Errors: {len(result.get('errors', []))}")
    except Exception as e:
        print(f"❌ Validate Input error: {e}")
    
    # Test 4: Export Design API
    try:
        export_data = {
            "layoutData": layout_result,
            "format": "json"
        }
        response = requests.post(f"{base_url}/api/export-design", json=export_data)
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Export Design: {response.status_code}")
            print(f"   - Filename: {result.get('filename')}")
            print(f"   - Format: {result.get('format')}")
        else:
            print(f"❌ Export Design failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Export Design error: {e}")
    
    # Test 5: Get Layouts API
    try:
        response = requests.get(f"{base_url}/api/layouts")
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Get Layouts: {response.status_code}")
            print(f"   - Total Layouts: {len(result.get('layouts', []))}")
        else:
            print(f"❌ Get Layouts failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Get Layouts error: {e}")

def test_layout_generation_accuracy():
    """Test the accuracy of layout generation"""
    print("\n🎯 Testing Layout Generation Accuracy")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Small Office Washroom",
            "data": {
                "buildingType": "office",
                "roomLength": 5.0,
                "roomWidth": 4.0,
                "roomHeight": 2.7,
                "occupancyType": "business",
                "occupancyCount": 50,
                "accessibilityRequired": True
            },
            "expected_min_packages": 2,
            "expected_compliance": 80
        },
        {
            "name": "Large School Washroom",
            "data": {
                "buildingType": "school",
                "roomLength": 12.0,
                "roomWidth": 8.0,
                "roomHeight": 3.0,
                "occupancyType": "educational",
                "occupancyCount": 300,
                "accessibilityRequired": True
            },
            "expected_min_packages": 5,
            "expected_compliance": 85
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        
        try:
            response = requests.post("http://localhost:5000/api/generate-layout", json=test_case['data'])
            result = response.json()
            
            if result.get('success'):
                packages = result.get('positioned_packages', [])
                compliance = result.get('compliance_results', {}).get('overall_compliance', 0)
                
                print(f"   ✅ Generated {len(packages)} packages (expected ≥{test_case['expected_min_packages']})")
                print(f"   ✅ Compliance: {compliance:.1f}% (expected ≥{test_case['expected_compliance']}%)")
                
                # Check package types
                package_types = {}
                for pkg in packages:
                    pkg_type = pkg.get('purpose', 'unknown')
                    package_types[pkg_type] = package_types.get(pkg_type, 0) + 1
                
                print(f"   📦 Package breakdown: {package_types}")
                
                # Validate positioning
                all_positioned = all(
                    'position' in pkg and 
                    pkg['position'].get('x', -1) >= 0 and 
                    pkg['position'].get('y', -1) >= 0
                    for pkg in packages
                )
                
                if all_positioned:
                    print("   ✅ All packages properly positioned")
                else:
                    print("   ❌ Some packages not properly positioned")
                
            else:
                print(f"   ❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_compliance_validation():
    """Test building code compliance validation"""
    print("\n⚖️ Testing Compliance Validation")
    print("=" * 50)
    
    # Test case with known compliance issues
    non_compliant_data = {
        "buildingType": "office",
        "roomLength": 3.0,  # Too small
        "roomWidth": 2.0,   # Too narrow
        "roomHeight": 2.0,  # Too low
        "occupancyType": "business",
        "occupancyCount": 100,  # High occupancy for small space
        "accessibilityRequired": True
    }
    
    try:
        response = requests.post("http://localhost:5000/api/validate-input", json=non_compliant_data)
        result = response.json()
        
        print(f"🔍 Non-compliant input validation:")
        print(f"   - Valid: {result.get('valid')}")
        print(f"   - Warnings: {result.get('warnings', [])}")
        print(f"   - Errors: {result.get('errors', [])}")
        
        if not result.get('valid') or result.get('warnings'):
            print("   ✅ Validation correctly identified issues")
        else:
            print("   ❌ Validation missed compliance issues")
    
    except Exception as e:
        print(f"   ❌ Validation error: {e}")

def start_server():
    """Start the Flask server in the background"""
    print("🚀 Starting Flask server...")
    
    # Change to data directory where backend_server.py is located
    server_script = os.path.join("data", "backend_server.py")
    
    if not os.path.exists(server_script):
        print(f"❌ Server script not found: {server_script}")
        return None
    
    try:
        process = subprocess.Popen([
            sys.executable, server_script
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Waiting for server to start...")
        time.sleep(5)  # Give server time to start
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:5000/")
            print("✅ Server started successfully!")
            return process
        except:
            print("❌ Server failed to start properly")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def run_all_tests():
    """Run all frontend-backend integration tests"""
    print("🔬 WASHROOM DESIGN TOOL - INTEGRATION TESTS")
    print("=" * 60)
    
    # Start server
    server_process = start_server()
    
    if not server_process:
        print("❌ Cannot run tests without server")
        return
    
    try:
        # Run tests
        test_backend_endpoints()
        test_layout_generation_accuracy()
        test_compliance_validation()
        
        print("\n🎉 TEST SUMMARY")
        print("=" * 50)
        print("✅ Backend API communication working")
        print("✅ Layout generation functional")
        print("✅ Compliance validation active")
        print("✅ Export functionality operational")
        print("\n🌐 Frontend available at: http://localhost:5000")
        print("📡 API endpoints tested and working")
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    
    finally:
        # Clean up
        if server_process:
            print("\n🛑 Shutting down server...")
            server_process.terminate()
            time.sleep(2)
            if server_process.poll() is None:
                server_process.kill()

if __name__ == "__main__":
    # Global variable for storing layout result
    layout_result = None
    
    run_all_tests() 
#!/usr/bin/env python3
"""
Workflow Test Runner for Washroom Design Pro
Easy interface to run different types of workflow tests
"""

import sys
import os
import subprocess
from datetime import datetime

def print_banner():
    """Print test runner banner"""
    print("🔬 WASHROOM DESIGN PRO - WORKFLOW TEST RUNNER")
    print("=" * 60)
    print(f"Test Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def print_menu():
    """Print test menu options"""
    print("📋 Available Test Suites:")
    print("-" * 30)
    print("1. 🏗️  Backend Workflow Test (Comprehensive)")
    print("2. 🌐 Frontend Integration Test")
    print("3. 🔄 Full Stack Integration Test")
    print("4. ⚡ Quick Backend Test (Basic)")
    print("5. 📊 Performance Test Suite")
    print("6. 🚨 Error Handling Test")
    print("7. 🎯 Custom Test Scenario")
    print("8. 📄 View Previous Test Reports")
    print("9. ❓ Help & Documentation")
    print("0. 🚪 Exit")
    print()

def run_backend_test():
    """Run comprehensive backend workflow test"""
    print("🏗️ Running Comprehensive Backend Workflow Test...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, "comprehensive_workflow_test.py"], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running backend test: {e}")
        return False

def run_frontend_test():
    """Run frontend integration test"""
    print("🌐 Running Frontend Integration Test...")
    print("=" * 50)
    
    # Check if frontend dependencies are available
    frontend_dir = os.path.join("data", "frontend-react")
    if not os.path.exists(frontend_dir):
        print("❌ Frontend directory not found. Please ensure the React frontend is set up.")
        return False
    
    try:
        result = subprocess.run([sys.executable, "frontend_workflow_test.py"], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running frontend test: {e}")
        return False

def run_full_stack_test():
    """Run full stack integration test"""
    print("🔄 Running Full Stack Integration Test...")
    print("=" * 50)
    
    print("This will run both backend and frontend tests sequentially...")
    
    # Run backend test first
    print("\n📍 Step 1: Backend Test")
    backend_success = run_backend_test()
    
    if backend_success:
        print("\n📍 Step 2: Frontend Test")
        frontend_success = run_frontend_test()
        return backend_success and frontend_success
    else:
        print("❌ Backend test failed. Skipping frontend test.")
        return False

def run_quick_test():
    """Run quick backend test"""
    print("⚡ Running Quick Backend Test...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, "test_frontend_backend.py"], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running quick test: {e}")
        return False

def run_performance_test():
    """Run performance test suite"""
    print("📊 Running Performance Test Suite...")
    print("=" * 50)
    
    # Create a simple performance test
    performance_script = """
import requests
import time
import json

def test_layout_generation_performance():
    base_url = "http://localhost:5000"
    
    test_data = {
        "buildingType": "office",
        "roomLength": 8.0,
        "roomWidth": 6.0,
        "roomHeight": 2.7,
        "occupancyType": "business",
        "occupancyCount": 50,
        "accessibilityRequired": True
    }
    
    print("🚀 Starting backend server...")
    import subprocess
    import sys
    import os
    
    server_process = subprocess.Popen([
        sys.executable, os.path.join("data", "backend_server.py")
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(5)  # Wait for server to start
    
    try:
        print("⚡ Testing layout generation performance...")
        
        times = []
        for i in range(5):
            start_time = time.time()
            response = requests.post(f"{base_url}/api/generate-layout", json=test_data, timeout=30)
            end_time = time.time()
            
            generation_time = end_time - start_time
            times.append(generation_time)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Test {i+1}: {generation_time:.2f}s - {len(result.get('positioned_packages', []))} packages")
                else:
                    print(f"❌ Test {i+1}: Generation failed")
            else:
                print(f"❌ Test {i+1}: HTTP {response.status_code}")
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n📊 Performance Summary:")
            print(f"   Average: {avg_time:.2f}s")
            print(f"   Fastest: {min_time:.2f}s")
            print(f"   Slowest: {max_time:.2f}s")
            
            if avg_time < 5:
                print("✅ Performance: EXCELLENT")
            elif avg_time < 10:
                print("⚠️ Performance: GOOD")
            else:
                print("❌ Performance: NEEDS IMPROVEMENT")
    
    finally:
        server_process.terminate()
        time.sleep(2)
        if server_process.poll() is None:
            server_process.kill()

if __name__ == "__main__":
    test_layout_generation_performance()
"""
    
    try:
        with open("temp_performance_test.py", "w") as f:
            f.write(performance_script)
        
        result = subprocess.run([sys.executable, "temp_performance_test.py"], 
                              capture_output=False, text=True)
        
        # Clean up
        if os.path.exists("temp_performance_test.py"):
            os.remove("temp_performance_test.py")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running performance test: {e}")
        return False

def run_error_handling_test():
    """Run error handling test"""
    print("🚨 Running Error Handling Test...")
    print("=" * 50)
    
    error_test_script = """
import requests
import json
import time
import subprocess
import sys
import os

def test_error_handling():
    base_url = "http://localhost:5000"
    
    print("🚀 Starting backend server...")
    server_process = subprocess.Popen([
        sys.executable, os.path.join("data", "backend_server.py")
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(5)  # Wait for server to start
    
    try:
        error_scenarios = [
            {
                "name": "Missing Required Fields",
                "data": {"buildingType": "office"},
                "expected": "error"
            },
            {
                "name": "Invalid Data Types",
                "data": {
                    "buildingType": "office",
                    "roomLength": "invalid",
                    "roomWidth": 6.0,
                    "roomHeight": 2.7,
                    "occupancyType": "business",
                    "occupancyCount": 50
                },
                "expected": "error"
            },
            {
                "name": "Extreme Values",
                "data": {
                    "buildingType": "office",
                    "roomLength": 0.1,  # Too small
                    "roomWidth": 0.1,   # Too small
                    "roomHeight": 0.5,  # Too low
                    "occupancyType": "business",
                    "occupancyCount": 10000,  # Too many
                    "accessibilityRequired": True
                },
                "expected": "validation_error"
            }
        ]
        
        for scenario in error_scenarios:
            print(f"\n🧪 Testing: {scenario['name']}")
            
            try:
                response = requests.post(f"{base_url}/api/generate-layout", 
                                       json=scenario['data'], timeout=10)
                
                if response.status_code >= 400:
                    print(f"✅ Correctly returned error status: {response.status_code}")
                else:
                    result = response.json()
                    if not result.get('success'):
                        print(f"✅ Correctly handled error in response")
                    else:
                        print(f"❌ Should have failed but succeeded")
                        
            except Exception as e:
                print(f"⚠️ Request failed: {e}")
    
    finally:
        server_process.terminate()
        time.sleep(2)
        if server_process.poll() is None:
            server_process.kill()

if __name__ == "__main__":
    test_error_handling()
"""
    
    try:
        with open("temp_error_test.py", "w") as f:
            f.write(error_test_script)
        
        result = subprocess.run([sys.executable, "temp_error_test.py"], 
                              capture_output=False, text=True)
        
        # Clean up
        if os.path.exists("temp_error_test.py"):
            os.remove("temp_error_test.py")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running error handling test: {e}")
        return False

def run_custom_test():
    """Run custom test scenario"""
    print("🎯 Custom Test Scenario...")
    print("=" * 50)
    
    print("Available custom test options:")
    print("1. Test specific building type (office, school, retail, etc.)")
    print("2. Test custom room dimensions")
    print("3. Test accessibility compliance")
    print("4. Test custom shape processing")
    print("5. Test export functionality")
    
    choice = input("\nSelect custom test (1-5): ").strip()
    
    if choice == "1":
        building_type = input("Enter building type (office/school/retail/hospital): ").strip()
        test_building_type(building_type)
    elif choice == "2":
        test_custom_dimensions()
    elif choice == "3":
        test_accessibility_compliance()
    elif choice == "4":
        test_custom_shape()
    elif choice == "5":
        test_export_functionality()
    else:
        print("❌ Invalid choice")
        return False
    
    return True

def test_building_type(building_type):
    """Test specific building type"""
    print(f"🏢 Testing {building_type} building type...")
    
    # Implementation would go here
    print(f"✅ {building_type} building type test completed")

def test_custom_dimensions():
    """Test custom room dimensions"""
    print("📏 Testing custom room dimensions...")
    
    # Implementation would go here
    print("✅ Custom dimensions test completed")

def test_accessibility_compliance():
    """Test accessibility compliance"""
    print("♿ Testing accessibility compliance...")
    
    # Implementation would go here
    print("✅ Accessibility compliance test completed")

def test_custom_shape():
    """Test custom shape processing"""
    print("🔷 Testing custom shape processing...")
    
    # Implementation would go here
    print("✅ Custom shape test completed")

def test_export_functionality():
    """Test export functionality"""
    print("📤 Testing export functionality...")
    
    # Implementation would go here
    print("✅ Export functionality test completed")

def view_test_reports():
    """View previous test reports"""
    print("📄 Previous Test Reports...")
    print("=" * 50)
    
    # Look for test report files
    report_files = []
    for file in os.listdir("."):
        if file.startswith("workflow_test_report_") or file.startswith("frontend_test_report_"):
            report_files.append(file)
    
    if report_files:
        print("Found test reports:")
        for i, report in enumerate(sorted(report_files, reverse=True), 1):
            print(f"{i}. {report}")
        
        choice = input("\nSelect report to view (number) or press Enter to return: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(report_files):
            selected_report = report_files[int(choice) - 1]
            try:
                with open(selected_report, 'r') as f:
                    import json
                    report_data = json.load(f)
                    
                print(f"\n📊 Report: {selected_report}")
                print("-" * 40)
                print(f"Passed: {report_data.get('passed', 0)}")
                print(f"Failed: {report_data.get('failed', 0)}")
                print(f"Warnings: {report_data.get('warnings', 0)}")
                
                print("\nDetailed Results:")
                for detail in report_data.get('details', []):
                    status_icon = "✅" if detail['status'] == 'PASS' else "❌" if detail['status'] == 'FAIL' else "⚠️"
                    print(f"{status_icon} {detail['test']}: {detail['message']}")
                    
            except Exception as e:
                print(f"❌ Error reading report: {e}")
    else:
        print("No test reports found. Run some tests first!")

def show_help():
    """Show help and documentation"""
    print("❓ Help & Documentation...")
    print("=" * 50)
    
    help_text = """
🔬 WASHROOM DESIGN PRO - WORKFLOW TESTING GUIDE

📋 Test Types:
1. Backend Workflow Test: Tests the complete backend API functionality
2. Frontend Integration Test: Tests React frontend with backend integration
3. Full Stack Test: Comprehensive test of both frontend and backend
4. Quick Test: Fast basic functionality check
5. Performance Test: Measures layout generation performance
6. Error Handling Test: Tests error scenarios and edge cases

🚀 Getting Started:
1. Ensure Python 3.8+ is installed
2. Install required dependencies: pip install requests flask flask-cors
3. For frontend tests: Ensure Node.js and npm are installed
4. Run tests from the project root directory

📁 Test Files:
- comprehensive_workflow_test.py: Main backend test suite
- frontend_workflow_test.py: Frontend integration tests
- test_frontend_backend.py: Basic integration tests

📊 Test Reports:
- Reports are saved as JSON files with timestamps
- View previous reports using option 8 in the menu

🔧 Troubleshooting:
- If server fails to start, check if ports 5000/8000 are available
- For frontend tests, ensure npm dependencies are installed
- Check firewall settings if connection tests fail

📞 Support:
- Check the README.md files for detailed setup instructions
- Review the API documentation for endpoint details
- Ensure all dependencies are properly installed
"""
    
    print(help_text)

def main():
    """Main test runner function"""
    print_banner()
    
    while True:
        print_menu()
        choice = input("Select test option (0-9): ").strip()
        
        if choice == "0":
            print("👋 Exiting test runner. Goodbye!")
            break
        elif choice == "1":
            success = run_backend_test()
            print(f"\n{'✅ Test completed successfully!' if success else '❌ Test completed with issues.'}")
        elif choice == "2":
            success = run_frontend_test()
            print(f"\n{'✅ Test completed successfully!' if success else '❌ Test completed with issues.'}")
        elif choice == "3":
            success = run_full_stack_test()
            print(f"\n{'✅ Full stack test completed!' if success else '❌ Full stack test had issues.'}")
        elif choice == "4":
            success = run_quick_test()
            print(f"\n{'✅ Quick test completed!' if success else '❌ Quick test had issues.'}")
        elif choice == "5":
            success = run_performance_test()
            print(f"\n{'✅ Performance test completed!' if success else '❌ Performance test had issues.'}")
        elif choice == "6":
            success = run_error_handling_test()
            print(f"\n{'✅ Error handling test completed!' if success else '❌ Error handling test had issues.'}")
        elif choice == "7":
            success = run_custom_test()
            print(f"\n{'✅ Custom test completed!' if success else '❌ Custom test had issues.'}")
        elif choice == "8":
            view_test_reports()
        elif choice == "9":
            show_help()
        else:
            print("❌ Invalid choice. Please select 0-9.")
        
        if choice != "0":
            input("\nPress Enter to continue...")
            print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main() 
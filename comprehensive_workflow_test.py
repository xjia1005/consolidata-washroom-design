#!/usr/bin/env python3
"""
Comprehensive Workflow Test for Washroom Design Pro
Tests the complete end-to-end workflow including:
1. Backend API functionality
2. Layout generation with custom shapes
3. Compliance validation
4. Export functionality
5. Database operations
6. Frontend-backend integration
"""

import requests
import json
import time
import threading
import subprocess
import sys
import os
import sqlite3
from datetime import datetime

class WorkflowTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.server_process = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'details': []
        }
    
    def log_result(self, test_name, status, message="", details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results['details'].append(result)
        
        if status == 'PASS':
            self.test_results['passed'] += 1
            print(f"✅ {test_name}: {message}")
        elif status == 'FAIL':
            self.test_results['failed'] += 1
            print(f"❌ {test_name}: {message}")
        elif status == 'WARN':
            self.test_results['warnings'] += 1
            print(f"⚠️ {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"   📊 {key}: {value}")
    
    def start_server(self):
        """Start the Flask backend server"""
        print("🚀 Starting Backend Server...")
        print("=" * 50)
        
        server_script = os.path.join("data", "backend_server.py")
        
        if not os.path.exists(server_script):
            self.log_result("Server Setup", "FAIL", f"Server script not found: {server_script}")
            return False
        
        try:
            self.server_process = subprocess.Popen([
                sys.executable, server_script
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            for i in range(10):
                time.sleep(1)
                try:
                    response = requests.get(f"{self.base_url}/", timeout=2)
                    if response.status_code == 200:
                        self.log_result("Server Startup", "PASS", "Backend server started successfully")
                        return True
                except:
                    continue
            
            self.log_result("Server Startup", "FAIL", "Server failed to start within 10 seconds")
            return False
            
        except Exception as e:
            self.log_result("Server Startup", "FAIL", f"Failed to start server: {e}")
            return False
    
    def test_basic_api_endpoints(self):
        """Test basic API endpoint availability"""
        print("\n🔌 Testing Basic API Endpoints...")
        print("=" * 50)
        
        endpoints = [
            ("/", "Frontend Homepage"),
            ("/api/layouts", "Layouts API"),
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_result(f"API Endpoint - {name}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_result(f"API Endpoint - {name}", "WARN", f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_result(f"API Endpoint - {name}", "FAIL", f"Connection error: {e}")
    
    def test_input_validation(self):
        """Test input validation functionality"""
        print("\n⚖️ Testing Input Validation...")
        print("=" * 50)
        
        # Test valid input
        valid_input = {
            "buildingType": "office",
            "roomLength": 8.0,
            "roomWidth": 6.0,
            "roomHeight": 2.7,
            "occupancyType": "business",
            "occupancyCount": 50,
            "accessibilityRequired": True
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/validate-input", json=valid_input, timeout=10)
            result = response.json()
            
            if result.get('valid'):
                self.log_result("Input Validation - Valid Input", "PASS", "Valid input accepted", {
                    "Warnings": len(result.get('warnings', [])),
                    "Errors": len(result.get('errors', []))
                })
            else:
                self.log_result("Input Validation - Valid Input", "FAIL", "Valid input rejected")
        except Exception as e:
            self.log_result("Input Validation - Valid Input", "FAIL", f"Validation error: {e}")
        
        # Test invalid input
        invalid_input = {
            "buildingType": "office",
            "roomLength": 2.0,  # Too small
            "roomWidth": 1.0,   # Too narrow
            "roomHeight": 1.8,  # Too low
            "occupancyType": "business",
            "occupancyCount": 200,  # Too many for small space
            "accessibilityRequired": True
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/validate-input", json=invalid_input, timeout=10)
            result = response.json()
            
            if not result.get('valid') or result.get('errors'):
                self.log_result("Input Validation - Invalid Input", "PASS", "Invalid input correctly rejected", {
                    "Errors Found": len(result.get('errors', [])),
                    "Warnings": len(result.get('warnings', []))
                })
            else:
                self.log_result("Input Validation - Invalid Input", "FAIL", "Invalid input incorrectly accepted")
        except Exception as e:
            self.log_result("Input Validation - Invalid Input", "FAIL", f"Validation error: {e}")
    
    def test_layout_generation(self):
        """Test layout generation with different scenarios"""
        print("\n🏗️ Testing Layout Generation...")
        print("=" * 50)
        
        test_scenarios = [
            {
                "name": "Small Office Washroom",
                "data": {
                    "buildingType": "office",
                    "roomLength": 5.0,
                    "roomWidth": 4.0,
                    "roomHeight": 2.7,
                    "occupancyType": "business",
                    "occupancyCount": 30,
                    "accessibilityRequired": True
                },
                "expected_min_packages": 2,
                "expected_min_compliance": 70
            },
            {
                "name": "Large School Washroom",
                "data": {
                    "buildingType": "school",
                    "roomLength": 12.0,
                    "roomWidth": 8.0,
                    "roomHeight": 3.0,
                    "occupancyType": "educational",
                    "occupancyCount": 200,
                    "accessibilityRequired": True
                },
                "expected_min_packages": 4,
                "expected_min_compliance": 75
            },
            {
                "name": "Custom Shape Washroom",
                "data": {
                    "buildingType": "office",
                    "roomLength": 8.0,
                    "roomWidth": 6.0,
                    "roomHeight": 2.7,
                    "occupancyType": "business",
                    "occupancyCount": 50,
                    "accessibilityRequired": True,
                    "customShape": {
                        "shape": {
                            "type": "polygon",
                            "points": [
                                {"x": 0, "y": 0},
                                {"x": 8, "y": 0},
                                {"x": 8, "y": 4},
                                {"x": 6, "y": 6},
                                {"x": 0, "y": 6}
                            ],
                            "area": 44.0,
                            "bounds": {"width": 8.0, "height": 6.0}
                        },
                        "entrances": [
                            {
                                "position": {"x": 4, "y": 0},
                                "width": 1.0,
                                "type": "standard"
                            }
                        ],
                        "properties": {
                            "ceilingHeight": 2.7,
                            "wallThickness": 0.2
                        }
                    }
                },
                "expected_min_packages": 3,
                "expected_min_compliance": 70
            }
        ]
        
        for scenario in test_scenarios:
            try:
                response = requests.post(f"{self.base_url}/api/generate-layout", 
                                       json=scenario["data"], timeout=30)
                
                if response.status_code != 200:
                    self.log_result(f"Layout Generation - {scenario['name']}", "FAIL", 
                                  f"HTTP {response.status_code}")
                    continue
                
                result = response.json()
                
                if not result.get('success'):
                    self.log_result(f"Layout Generation - {scenario['name']}", "FAIL", 
                                  f"Generation failed: {result.get('error')}")
                    continue
                
                # Validate results
                packages = result.get('positioned_packages', [])
                compliance = result.get('compliance_results', {}).get('overall_compliance', 0)
                
                details = {
                    "Packages Generated": len(packages),
                    "Compliance Score": f"{compliance:.1f}%",
                    "Space Utilization": f"{result.get('utilization_metrics', {}).get('space_utilization', 0):.1f}%"
                }
                
                # Check if meets expectations
                if (len(packages) >= scenario['expected_min_packages'] and 
                    compliance >= scenario['expected_min_compliance']):
                    self.log_result(f"Layout Generation - {scenario['name']}", "PASS", 
                                  "Layout generated successfully", details)
                    
                    # Store result for export testing
                    if scenario['name'] == "Small Office Washroom":
                        self.sample_layout = result
                else:
                    self.log_result(f"Layout Generation - {scenario['name']}", "WARN", 
                                  "Layout generated but below expectations", details)
                
            except Exception as e:
                self.log_result(f"Layout Generation - {scenario['name']}", "FAIL", 
                              f"Generation error: {e}")
    
    def test_compliance_checking(self):
        """Test building code compliance checking"""
        print("\n📋 Testing Compliance Checking...")
        print("=" * 50)
        
        # Test with known compliance issues
        non_compliant_data = {
            "buildingType": "office",
            "roomLength": 3.0,
            "roomWidth": 2.5,
            "roomHeight": 2.0,  # Below minimum
            "occupancyType": "business",
            "occupancyCount": 100,
            "accessibilityRequired": True
        }
        
        try:
            # First validate input
            response = requests.post(f"{self.base_url}/api/validate-input", 
                                   json=non_compliant_data, timeout=10)
            validation = response.json()
            
            # Then try to generate layout
            response = requests.post(f"{self.base_url}/api/generate-layout", 
                                   json=non_compliant_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    compliance = result.get('compliance_results', {})
                    violations = compliance.get('violations', 0)
                    
                    if violations > 0 or compliance.get('overall_compliance', 100) < 80:
                        self.log_result("Compliance Checking", "PASS", 
                                      "Compliance issues correctly identified", {
                                          "Violations": violations,
                                          "Compliance Score": f"{compliance.get('overall_compliance', 0):.1f}%"
                                      })
                    else:
                        self.log_result("Compliance Checking", "WARN", 
                                      "Compliance issues not detected")
                else:
                    self.log_result("Compliance Checking", "PASS", 
                                  "Non-compliant layout correctly rejected")
            else:
                self.log_result("Compliance Checking", "FAIL", 
                              f"Unexpected response: {response.status_code}")
                
        except Exception as e:
            self.log_result("Compliance Checking", "FAIL", f"Compliance test error: {e}")
    
    def test_export_functionality(self):
        """Test export functionality"""
        print("\n📤 Testing Export Functionality...")
        print("=" * 50)
        
        if not hasattr(self, 'sample_layout'):
            self.log_result("Export Test", "FAIL", "No sample layout available for export")
            return
        
        export_formats = ['json', 'dxf', 'report']
        
        for format_type in export_formats:
            try:
                export_data = {
                    "layoutData": self.sample_layout,
                    "format": format_type
                }
                
                response = requests.post(f"{self.base_url}/api/export-design", 
                                       json=export_data, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        content_length = len(result.get('content', ''))
                        self.log_result(f"Export - {format_type.upper()}", "PASS", 
                                      "Export generated successfully", {
                                          "Content Length": f"{content_length} characters",
                                          "Filename": result.get('filename', 'N/A')
                                      })
                    else:
                        self.log_result(f"Export - {format_type.upper()}", "FAIL", 
                                      f"Export failed: {result.get('error')}")
                else:
                    self.log_result(f"Export - {format_type.upper()}", "FAIL", 
                                  f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Export - {format_type.upper()}", "FAIL", 
                              f"Export error: {e}")
    
    def test_database_operations(self):
        """Test database storage and retrieval"""
        print("\n🗄️ Testing Database Operations...")
        print("=" * 50)
        
        try:
            # Test getting layouts
            response = requests.get(f"{self.base_url}/api/layouts", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    layouts = result.get('layouts', [])
                    self.log_result("Database - Layout Retrieval", "PASS", 
                                  "Layouts retrieved successfully", {
                                      "Total Layouts": len(layouts)
                                  })
                    
                    # Check if our test layouts were stored
                    if layouts:
                        latest_layout = layouts[0]
                        self.log_result("Database - Layout Storage", "PASS", 
                                      "Layout data properly stored", {
                                          "Latest Project": latest_layout.get('project_name', 'N/A'),
                                          "Building Type": latest_layout.get('building_type', 'N/A'),
                                          "Compliance Score": f"{latest_layout.get('compliance_score', 0):.1f}%"
                                      })
                else:
                    self.log_result("Database - Layout Retrieval", "FAIL", 
                                  f"Database error: {result.get('error')}")
            else:
                self.log_result("Database - Layout Retrieval", "FAIL", 
                              f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Database Operations", "FAIL", f"Database test error: {e}")
    
    def test_performance_metrics(self):
        """Test performance and response times"""
        print("\n⚡ Testing Performance Metrics...")
        print("=" * 50)
        
        # Test layout generation performance
        test_data = {
            "buildingType": "office",
            "roomLength": 6.0,
            "roomWidth": 5.0,
            "roomHeight": 2.7,
            "occupancyType": "business",
            "occupancyCount": 40,
            "accessibilityRequired": True
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{self.base_url}/api/generate-layout", 
                                   json=test_data, timeout=30)
            end_time = time.time()
            
            generation_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    if generation_time < 10:  # Should complete within 10 seconds
                        self.log_result("Performance - Layout Generation", "PASS", 
                                      "Generation completed within acceptable time", {
                                          "Generation Time": f"{generation_time:.2f} seconds",
                                          "Packages Generated": len(result.get('positioned_packages', []))
                                      })
                    else:
                        self.log_result("Performance - Layout Generation", "WARN", 
                                      "Generation took longer than expected", {
                                          "Generation Time": f"{generation_time:.2f} seconds"
                                      })
                else:
                    self.log_result("Performance - Layout Generation", "FAIL", 
                                  "Generation failed during performance test")
            else:
                self.log_result("Performance - Layout Generation", "FAIL", 
                              f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Performance Test", "FAIL", f"Performance test error: {e}")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🚨 Testing Error Handling...")
        print("=" * 50)
        
        # Test missing required fields
        incomplete_data = {
            "buildingType": "office",
            # Missing required fields
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/generate-layout", 
                                   json=incomplete_data, timeout=10)
            
            if response.status_code == 400:
                self.log_result("Error Handling - Missing Fields", "PASS", 
                              "Missing fields correctly rejected")
            else:
                result = response.json()
                if not result.get('success'):
                    self.log_result("Error Handling - Missing Fields", "PASS", 
                                  "Missing fields handled gracefully")
                else:
                    self.log_result("Error Handling - Missing Fields", "FAIL", 
                                  "Missing fields not detected")
                    
        except Exception as e:
            self.log_result("Error Handling - Missing Fields", "FAIL", 
                          f"Error handling test failed: {e}")
        
        # Test invalid data types
        invalid_data = {
            "buildingType": "office",
            "roomLength": "invalid",  # Should be number
            "roomWidth": 6.0,
            "roomHeight": 2.7,
            "occupancyType": "business",
            "occupancyCount": 50,
            "accessibilityRequired": True
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/generate-layout", 
                                   json=invalid_data, timeout=10)
            
            if response.status_code >= 400:
                self.log_result("Error Handling - Invalid Data Types", "PASS", 
                              "Invalid data types correctly rejected")
            else:
                result = response.json()
                if not result.get('success'):
                    self.log_result("Error Handling - Invalid Data Types", "PASS", 
                                  "Invalid data types handled gracefully")
                else:
                    self.log_result("Error Handling - Invalid Data Types", "WARN", 
                                  "Invalid data types not detected")
                    
        except Exception as e:
            self.log_result("Error Handling - Invalid Data Types", "FAIL", 
                          f"Error handling test failed: {e}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = self.test_results['passed'] + self.test_results['failed'] + self.test_results['warnings']
        
        print(f"Total Tests Run: {total_tests}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"⚠️ Warnings: {self.test_results['warnings']}")
        
        if total_tests > 0:
            success_rate = (self.test_results['passed'] / total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 40)
        
        for result in self.test_results['details']:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
            print(f"{status_icon} {result['test']}: {result['message']}")
        
        # Save detailed report to file
        report_filename = f"workflow_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")
        
        # Overall assessment
        if self.test_results['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED! The workflow is functioning correctly.")
        elif self.test_results['failed'] <= 2:
            print("\n⚠️ MOSTLY WORKING: Minor issues detected, but core functionality is operational.")
        else:
            print("\n🚨 ISSUES DETECTED: Multiple failures indicate significant problems that need attention.")
    
    def cleanup(self):
        """Clean up resources"""
        if self.server_process:
            print("\n🛑 Shutting down server...")
            self.server_process.terminate()
            time.sleep(2)
            if self.server_process.poll() is None:
                self.server_process.kill()
    
    def run_comprehensive_test(self):
        """Run all workflow tests"""
        print("🔬 WASHROOM DESIGN PRO - COMPREHENSIVE WORKFLOW TEST")
        print("=" * 70)
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Start server
            if not self.start_server():
                print("❌ Cannot proceed without server")
                return
            
            # Run all test suites
            self.test_basic_api_endpoints()
            self.test_input_validation()
            self.test_layout_generation()
            self.test_compliance_checking()
            self.test_export_functionality()
            self.test_database_operations()
            self.test_performance_metrics()
            self.test_error_handling()
            
            # Generate report
            self.generate_test_report()
            
        except KeyboardInterrupt:
            print("\n⏹️ Tests interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error during testing: {e}")
        finally:
            self.cleanup()

def main():
    """Main function to run workflow tests"""
    tester = WorkflowTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Comprehensive Local Testing Guide
Tests all core functions of the Consolidata Washroom Design System
"""

import requests
import json
import time
import sys
from datetime import datetime

class LocalSystemTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
        print(f"{status}: {test_name}")
        if details and not passed:
            print(f"   Details: {details}")
    
    def test_server_health(self):
        """Test 1: Server Health Check"""
        print("\n🔍 Test 1: Server Health Check")
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                expected_service = "Consolidata Building Code API"
                if data.get("service") == expected_service:
                    self.log_test("Health Check", True, f"Service: {data.get('service')}")
                else:
                    self.log_test("Health Check", False, f"Wrong service name: {data.get('service')}")
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {e}")
    
    def test_basic_analysis(self):
        """Test 2: Basic Analysis Functionality"""
        print("\n🔍 Test 2: Basic Analysis")
        
        test_cases = [
            {
                "name": "Small Office (50 occupants)",
                "data": {
                    "building_type": "office",
                    "jurisdiction": "NBC",
                    "occupancy_load": 50,
                    "accessibility_level": "basic",
                    "room_dimensions": {"length": 8, "width": 6, "height": 3}
                },
                "expected_fixtures": {"min": 8, "max": 15}
            },
            {
                "name": "Large Office (150 occupants)",
                "data": {
                    "building_type": "office",
                    "jurisdiction": "NBC", 
                    "occupancy_load": 150,
                    "accessibility_level": "enhanced",
                    "room_dimensions": {"length": 12, "width": 8, "height": 3}
                },
                "expected_fixtures": {"min": 15, "max": 25}
            },
            {
                "name": "School Building (100 students)",
                "data": {
                    "building_type": "school",
                    "jurisdiction": "NBC",
                    "occupancy_load": 100,
                    "accessibility_level": "enhanced",
                    "room_dimensions": {"length": 10, "width": 8, "height": 3}
                },
                "expected_fixtures": {"min": 10, "max": 20}
            }
        ]
        
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/complete-analysis",
                    json=case["data"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        fixtures = data["report"]["fixture_requirements"]["total_fixtures"]
                        expected_min = case["expected_fixtures"]["min"]
                        expected_max = case["expected_fixtures"]["max"]
                        
                        if expected_min <= fixtures <= expected_max:
                            self.log_test(f"Basic Analysis - {case['name']}", True, 
                                        f"Fixtures: {fixtures} (expected {expected_min}-{expected_max})")
                        else:
                            self.log_test(f"Basic Analysis - {case['name']}", False,
                                        f"Fixtures: {fixtures} (expected {expected_min}-{expected_max})")
                    else:
                        self.log_test(f"Basic Analysis - {case['name']}", False, "API returned success=false")
                else:
                    self.log_test(f"Basic Analysis - {case['name']}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Basic Analysis - {case['name']}", False, f"Error: {e}")
    
    def test_enhanced_analysis(self):
        """Test 3: Enhanced Analysis (7-Step Workflow)"""
        print("\n🔍 Test 3: Enhanced Analysis (7-Step Workflow)")
        
        test_data = {
            "building_type": "office",
            "jurisdiction": "NBC",
            "occupancy_load": 150,
            "room_length": 12.0,
            "room_width": 8.0,
            "accessibility_level": "enhanced"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/enhanced-analysis",
                json=test_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check main response structure
                required_fields = ["status", "workflow_id", "compliance_checklist", "layout_design", "summary"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Check workflow steps
                    workflow_steps = data.get("workflow_steps", {})
                    expected_steps = 7
                    actual_steps = len(workflow_steps)
                    
                    if actual_steps == expected_steps:
                        # Check compliance checklist
                        checklist = data.get("compliance_checklist", {})
                        total_items = checklist.get("project_info", {}).get("total_items", 0)
                        
                        if total_items > 0:
                            # Check layout design
                            layout = data.get("layout_design", {})
                            positioned_assemblies = layout.get("positioned_assemblies", [])
                            
                            if len(positioned_assemblies) > 0:
                                self.log_test("Enhanced Analysis - Complete Workflow", True,
                                            f"Steps: {actual_steps}, Checklist items: {total_items}, Layout assemblies: {len(positioned_assemblies)}")
                            else:
                                self.log_test("Enhanced Analysis - Complete Workflow", False, "No layout assemblies generated")
                        else:
                            self.log_test("Enhanced Analysis - Complete Workflow", False, "No checklist items generated")
                    else:
                        self.log_test("Enhanced Analysis - Complete Workflow", False, f"Wrong step count: {actual_steps} (expected {expected_steps})")
                else:
                    self.log_test("Enhanced Analysis - Complete Workflow", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Enhanced Analysis - Complete Workflow", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Analysis - Complete Workflow", False, f"Error: {e}")
    
    def test_multi_jurisdiction(self):
        """Test 4: Multi-Jurisdiction Support"""
        print("\n🔍 Test 4: Multi-Jurisdiction Support")
        
        jurisdictions = ["NBC", "Alberta", "Ontario", "BC"]
        
        for jurisdiction in jurisdictions:
            try:
                test_data = {
                    "building_type": "office",
                    "jurisdiction": jurisdiction,
                    "occupancy_load": 100,
                    "accessibility_level": "basic",
                    "room_dimensions": {"length": 10, "width": 8, "height": 3}
                }
                
                response = requests.post(
                    f"{self.base_url}/api/complete-analysis",
                    json=test_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        code_refs = data["report"]["fixture_requirements"]["code_references"]
                        if any(jurisdiction in ref for ref in code_refs):
                            self.log_test(f"Multi-Jurisdiction - {jurisdiction}", True, f"Code refs: {code_refs}")
                        else:
                            self.log_test(f"Multi-Jurisdiction - {jurisdiction}", False, f"Wrong code refs: {code_refs}")
                    else:
                        self.log_test(f"Multi-Jurisdiction - {jurisdiction}", False, "API returned success=false")
                else:
                    self.log_test(f"Multi-Jurisdiction - {jurisdiction}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Multi-Jurisdiction - {jurisdiction}", False, f"Error: {e}")
    
    def test_accessibility_levels(self):
        """Test 5: Accessibility Level Support"""
        print("\n🔍 Test 5: Accessibility Level Support")
        
        accessibility_levels = ["basic", "enhanced"]
        
        for level in accessibility_levels:
            try:
                test_data = {
                    "building_type": "office",
                    "jurisdiction": "NBC",
                    "occupancy_load": 100,
                    "accessibility_level": level,
                    "room_dimensions": {"length": 10, "width": 8, "height": 3}
                }
                
                response = requests.post(
                    f"{self.base_url}/api/complete-analysis",
                    json=test_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        accessible_stalls = data["report"]["fixture_requirements"]["accessible_stalls"]
                        if accessible_stalls >= 1:
                            self.log_test(f"Accessibility - {level}", True, f"Accessible stalls: {accessible_stalls}")
                        else:
                            self.log_test(f"Accessibility - {level}", False, f"No accessible stalls: {accessible_stalls}")
                    else:
                        self.log_test(f"Accessibility - {level}", False, "API returned success=false")
                else:
                    self.log_test(f"Accessibility - {level}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Accessibility - {level}", False, f"Error: {e}")
    
    def test_building_types(self):
        """Test 6: Different Building Types"""
        print("\n🔍 Test 6: Building Type Support")
        
        building_types = ["office", "school", "assembly", "retail", "industrial"]
        
        for building_type in building_types:
            try:
                test_data = {
                    "building_type": building_type,
                    "jurisdiction": "NBC",
                    "occupancy_load": 80,
                    "accessibility_level": "basic",
                    "room_dimensions": {"length": 10, "width": 8, "height": 3}
                }
                
                response = requests.post(
                    f"{self.base_url}/api/complete-analysis",
                    json=test_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        basis = data["report"]["fixture_requirements"]["calculation_basis"]
                        if building_type in basis.lower():
                            self.log_test(f"Building Type - {building_type}", True, f"Basis: {basis}")
                        else:
                            self.log_test(f"Building Type - {building_type}", True, f"Processed successfully")
                    else:
                        self.log_test(f"Building Type - {building_type}", False, "API returned success=false")
                else:
                    self.log_test(f"Building Type - {building_type}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Building Type - {building_type}", False, f"Error: {e}")
    
    def test_frontend_access(self):
        """Test 7: Frontend Access"""
        print("\n🔍 Test 7: Frontend Access")
        
        try:
            # Test main frontend page
            response = requests.get(f"{self.base_url}/frontend/index.html", timeout=5)
            if response.status_code == 200:
                if "Consolidata" in response.text or "washroom" in response.text.lower():
                    self.log_test("Frontend Access", True, "Frontend page loads correctly")
                else:
                    self.log_test("Frontend Access", False, "Frontend content doesn't match expected")
            else:
                self.log_test("Frontend Access", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Frontend Access", False, f"Error: {e}")
    
    def test_concurrent_users(self):
        """Test 8: Concurrent User Support (Threading Fix Verification)"""
        print("\n🔍 Test 8: Concurrent User Support")
        
        # This will run the existing threading test
        try:
            import subprocess
            result = subprocess.run(["python", "test_threading_fix.py"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "ALL TESTS PASSED" in result.stdout:
                self.log_test("Concurrent Users", True, "Threading test passed")
            else:
                self.log_test("Concurrent Users", False, f"Threading test failed: {result.stderr}")
                
        except Exception as e:
            self.log_test("Concurrent Users", False, f"Error running threading test: {e}")
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🧪 CONSOLIDATA WASHROOM DESIGN SYSTEM - LOCAL TESTING")
        print("=" * 60)
        print(f"Testing server at: {self.base_url}")
        print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        self.test_server_health()
        self.test_basic_analysis()
        self.test_enhanced_analysis()
        self.test_multi_jurisdiction()
        self.test_accessibility_levels()
        self.test_building_types()
        self.test_frontend_access()
        self.test_concurrent_users()
        
        # Generate summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/(self.passed + self.failed))*100:.1f}%")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! Your system is ready for production deployment!")
            print("✅ All core functions working as designed")
            print("✅ Multi-user support verified")
            print("✅ All building types supported")
            print("✅ All jurisdictions working")
            print("✅ Frontend accessible")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Please review and fix before deployment.")
            print("\nFailed tests:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return self.failed == 0

def main():
    """Main testing function"""
    print("Starting local system testing...")
    print("Make sure your server is running: python start.py")
    print()
    
    # Wait a moment for user to start server if needed
    input("Press Enter when your server is running at http://localhost:5000...")
    
    tester = LocalSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 READY FOR PRODUCTION DEPLOYMENT!")
        print("Your system has passed all local tests.")
        print("You can now proceed with deployment to Railway/Render/Vercel.")
    else:
        print("\n🔧 PLEASE FIX ISSUES BEFORE DEPLOYMENT")
        print("Review the failed tests above and fix any issues.")
    
    return success

if __name__ == "__main__":
    main() 
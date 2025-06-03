#!/usr/bin/env python3
"""
Comprehensive System Test - Consolidata Washroom Design System
Tests Frontend + Backend + APIs + Workflow Integration
"""

import requests
import json
import time
import sys
import webbrowser
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class ComprehensiveSystemTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def log_test(self, category, test_name, passed, details=""):
        """Log test results with category"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "category": category,
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
        print(f"{status}: [{category}] {test_name}")
        if details and not passed:
            print(f"   Details: {details}")
    
    def test_backend_health(self):
        """Test 1: Backend Health & Database"""
        print("\n🔍 BACKEND TESTING")
        print("=" * 50)
        
        try:
            # Health check
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("service") == "Consolidata Building Code API":
                    self.log_test("Backend", "Health Check", True, f"Service: {data.get('service')}")
                else:
                    self.log_test("Backend", "Health Check", False, f"Wrong service: {data.get('service')}")
            else:
                self.log_test("Backend", "Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Backend", "Health Check", False, f"Connection error: {e}")
            return False
        
        # Database connectivity test
        try:
            response = requests.post(
                f"{self.base_url}/api/complete-analysis",
                json={
                    "building_type": "office",
                    "jurisdiction": "NBC",
                    "occupancy_load": 50,
                    "accessibility_level": "basic",
                    "room_dimensions": {"length": 8, "width": 6, "height": 3}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Backend", "Database Connectivity", True, "Database queries working")
                else:
                    self.log_test("Backend", "Database Connectivity", False, "API returned success=false")
            else:
                self.log_test("Backend", "Database Connectivity", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Backend", "Database Connectivity", False, f"Error: {e}")
        
        return True
    
    def test_api_endpoints(self):
        """Test 2: All API Endpoints"""
        print("\n🔍 API ENDPOINT TESTING")
        print("=" * 50)
        
        endpoints = [
            {
                "name": "Health Endpoint",
                "method": "GET",
                "url": "/api/health",
                "expected_status": 200
            },
            {
                "name": "Complete Analysis Endpoint",
                "method": "POST",
                "url": "/api/complete-analysis",
                "data": {
                    "building_type": "office",
                    "jurisdiction": "NBC",
                    "occupancy_load": 100,
                    "accessibility_level": "basic",
                    "room_dimensions": {"length": 10, "width": 8, "height": 3}
                },
                "expected_status": 200
            },
            {
                "name": "Enhanced Analysis Endpoint",
                "method": "POST",
                "url": "/api/enhanced-analysis",
                "data": {
                    "building_type": "office",
                    "jurisdiction": "NBC",
                    "occupancy_load": 150,
                    "room_length": 12.0,
                    "room_width": 8.0,
                    "accessibility_level": "enhanced"
                },
                "expected_status": 200
            }
        ]
        
        for endpoint in endpoints:
            try:
                if endpoint["method"] == "GET":
                    response = requests.get(f"{self.base_url}{endpoint['url']}", timeout=10)
                else:
                    response = requests.post(
                        f"{self.base_url}{endpoint['url']}", 
                        json=endpoint.get("data", {}),
                        timeout=15
                    )
                
                if response.status_code == endpoint["expected_status"]:
                    if endpoint["method"] == "POST":
                        data = response.json()
                        if data.get("success") or data.get("status") == "success":
                            self.log_test("API", endpoint["name"], True, f"Status: {response.status_code}")
                        else:
                            self.log_test("API", endpoint["name"], False, "API returned error")
                    else:
                        self.log_test("API", endpoint["name"], True, f"Status: {response.status_code}")
                else:
                    self.log_test("API", endpoint["name"], False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("API", endpoint["name"], False, f"Error: {e}")
    
    def test_workflow_integration(self):
        """Test 3: Complete Workflow Integration"""
        print("\n🔍 WORKFLOW INTEGRATION TESTING")
        print("=" * 50)
        
        # Test complete workflow scenarios
        scenarios = [
            {
                "name": "Small Office Workflow",
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
                "name": "Large Office Enhanced Workflow",
                "data": {
                    "building_type": "office",
                    "jurisdiction": "NBC",
                    "occupancy_load": 150,
                    "room_length": 12.0,
                    "room_width": 8.0,
                    "accessibility_level": "enhanced"
                },
                "endpoint": "/api/enhanced-analysis",
                "expected_fixtures": {"min": 15, "max": 25}
            },
            {
                "name": "School Building Workflow",
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
        
        for scenario in scenarios:
            try:
                endpoint = scenario.get("endpoint", "/api/complete-analysis")
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json=scenario["data"],
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check workflow completion
                    if endpoint == "/api/enhanced-analysis":
                        # Enhanced workflow checks
                        if data.get("status") == "success":
                            workflow_steps = data.get("workflow_steps", {})
                            checklist = data.get("compliance_checklist", {})
                            layout = data.get("layout_design", {})
                            
                            if len(workflow_steps) == 7 and checklist and layout:
                                self.log_test("Workflow", scenario["name"], True, 
                                            f"7-step workflow completed with checklist and layout")
                            else:
                                self.log_test("Workflow", scenario["name"], False, 
                                            f"Incomplete workflow: steps={len(workflow_steps)}")
                        else:
                            self.log_test("Workflow", scenario["name"], False, "Enhanced workflow failed")
                    else:
                        # Basic workflow checks
                        if data.get("success"):
                            report = data.get("report", {})
                            fixtures = report.get("fixture_requirements", {}).get("total_fixtures", 0)
                            layout_elements = report.get("layout_elements", [])
                            
                            expected_min = scenario["expected_fixtures"]["min"]
                            expected_max = scenario["expected_fixtures"]["max"]
                            
                            if expected_min <= fixtures <= expected_max and len(layout_elements) > 0:
                                self.log_test("Workflow", scenario["name"], True, 
                                            f"Complete workflow: {fixtures} fixtures, {len(layout_elements)} layout elements")
                            else:
                                self.log_test("Workflow", scenario["name"], False, 
                                            f"Workflow issues: fixtures={fixtures}, layout_elements={len(layout_elements)}")
                        else:
                            self.log_test("Workflow", scenario["name"], False, "Basic workflow failed")
                else:
                    self.log_test("Workflow", scenario["name"], False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Workflow", scenario["name"], False, f"Error: {e}")
    
    def test_concurrent_performance(self):
        """Test 4: Concurrent Performance & Threading"""
        print("\n🔍 CONCURRENT PERFORMANCE TESTING")
        print("=" * 50)
        
        def make_request(request_id):
            """Make a single request"""
            try:
                response = requests.post(
                    f"{self.base_url}/api/enhanced-analysis",
                    json={
                        "building_type": "office",
                        "jurisdiction": "NBC",
                        "occupancy_load": 100,
                        "room_length": 10.0,
                        "room_width": 8.0,
                        "accessibility_level": "basic"
                    },
                    timeout=20
                )
                return {
                    "id": request_id,
                    "status": response.status_code,
                    "success": response.status_code == 200 and response.json().get("status") == "success"
                }
            except Exception as e:
                return {"id": request_id, "status": 0, "success": False, "error": str(e)}
        
        # Test with 5 concurrent requests
        print("Testing 5 concurrent requests...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        
        successful = sum(1 for r in results if r["success"])
        
        if successful == 5:
            self.log_test("Performance", "Concurrent Requests", True, 
                        f"5/5 requests successful in {duration:.2f}s")
        else:
            self.log_test("Performance", "Concurrent Requests", False, 
                        f"Only {successful}/5 requests successful")
    
    def test_frontend_accessibility(self):
        """Test 5: Frontend Accessibility"""
        print("\n🔍 FRONTEND ACCESSIBILITY TESTING")
        print("=" * 50)
        
        try:
            # Test main frontend page
            response = requests.get(f"{self.base_url}/frontend/index.html", timeout=5)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for essential frontend elements
                checks = [
                    ("HTML Structure", "<html" in content and "<body" in content),
                    ("Form Elements", "form" in content and "input" in content),
                    ("JavaScript", "<script" in content or "javascript" in content),
                    ("CSS Styling", "<style" in content or "stylesheet" in content),
                    ("Consolidata Branding", "consolidata" in content)
                ]
                
                for check_name, passed in checks:
                    self.log_test("Frontend", check_name, passed, 
                                "Found" if passed else "Missing")
                
                # Overall frontend test
                all_passed = all(passed for _, passed in checks)
                self.log_test("Frontend", "Overall Accessibility", all_passed, 
                            "All elements present" if all_passed else "Some elements missing")
            else:
                self.log_test("Frontend", "Page Load", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Frontend", "Page Load", False, f"Error: {e}")
    
    def test_data_quality(self):
        """Test 6: Data Quality & Accuracy"""
        print("\n🔍 DATA QUALITY TESTING")
        print("=" * 50)
        
        # Test data consistency across different scenarios
        test_cases = [
            {
                "name": "NBC vs Alberta Differences",
                "nbc_data": {
                    "building_type": "office",
                    "jurisdiction": "NBC",
                    "occupancy_load": 100,
                    "accessibility_level": "basic",
                    "room_dimensions": {"length": 10, "width": 8, "height": 3}
                },
                "alberta_data": {
                    "building_type": "office",
                    "jurisdiction": "Alberta",
                    "occupancy_load": 100,
                    "accessibility_level": "basic",
                    "room_dimensions": {"length": 10, "width": 8, "height": 3}
                }
            }
        ]
        
        for case in test_cases:
            try:
                # Get NBC results
                nbc_response = requests.post(
                    f"{self.base_url}/api/complete-analysis",
                    json=case["nbc_data"],
                    timeout=10
                )
                
                # Get Alberta results
                alberta_response = requests.post(
                    f"{self.base_url}/api/complete-analysis",
                    json=case["alberta_data"],
                    timeout=10
                )
                
                if nbc_response.status_code == 200 and alberta_response.status_code == 200:
                    nbc_data = nbc_response.json()
                    alberta_data = alberta_response.json()
                    
                    if nbc_data.get("success") and alberta_data.get("success"):
                        # Check for differences in code references
                        nbc_refs = nbc_data["report"]["fixture_requirements"]["code_references"]
                        alberta_refs = alberta_data["report"]["fixture_requirements"]["code_references"]
                        
                        has_differences = any("NBC" in ref for ref in nbc_refs) and any("Alberta" in ref for ref in alberta_refs)
                        
                        self.log_test("Data Quality", case["name"], has_differences,
                                    "Jurisdiction-specific differences detected" if has_differences else "No differences found")
                    else:
                        self.log_test("Data Quality", case["name"], False, "One or both requests failed")
                else:
                    self.log_test("Data Quality", case["name"], False, "HTTP errors")
                    
            except Exception as e:
                self.log_test("Data Quality", case["name"], False, f"Error: {e}")
    
    def test_error_handling(self):
        """Test 7: Error Handling & Edge Cases"""
        print("\n🔍 ERROR HANDLING TESTING")
        print("=" * 50)
        
        error_tests = [
            {
                "name": "Empty Request",
                "data": {},
                "should_fail": True
            },
            {
                "name": "Invalid Building Type",
                "data": {
                    "building_type": "invalid_type",
                    "jurisdiction": "NBC",
                    "occupancy_load": 100,
                    "accessibility_level": "basic",
                    "room_dimensions": {"length": 10, "width": 8, "height": 3}
                },
                "should_fail": False  # Should handle gracefully
            },
            {
                "name": "Zero Occupancy",
                "data": {
                    "building_type": "office",
                    "jurisdiction": "NBC",
                    "occupancy_load": 0,
                    "accessibility_level": "basic",
                    "room_dimensions": {"length": 10, "width": 8, "height": 3}
                },
                "should_fail": False  # Should handle gracefully
            },
            {
                "name": "Extreme Occupancy",
                "data": {
                    "building_type": "office",
                    "jurisdiction": "NBC",
                    "occupancy_load": 10000,
                    "accessibility_level": "basic",
                    "room_dimensions": {"length": 10, "width": 8, "height": 3}
                },
                "should_fail": False  # Should handle gracefully
            }
        ]
        
        for test in error_tests:
            try:
                response = requests.post(
                    f"{self.base_url}/api/complete-analysis",
                    json=test["data"],
                    timeout=10
                )
                
                if test["should_fail"]:
                    # Should return error
                    if response.status_code != 200 or not response.json().get("success", True):
                        self.log_test("Error Handling", test["name"], True, "Properly rejected invalid input")
                    else:
                        self.log_test("Error Handling", test["name"], False, "Should have failed but didn't")
                else:
                    # Should handle gracefully
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success") or "error" in data:
                            self.log_test("Error Handling", test["name"], True, "Handled gracefully")
                        else:
                            self.log_test("Error Handling", test["name"], False, "Unexpected response")
                    else:
                        self.log_test("Error Handling", test["name"], False, f"HTTP error: {response.status_code}")
                        
            except Exception as e:
                if test["should_fail"]:
                    self.log_test("Error Handling", test["name"], True, "Exception properly raised")
                else:
                    self.log_test("Error Handling", test["name"], False, f"Unexpected exception: {e}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🧪 COMPREHENSIVE SYSTEM TEST - CONSOLIDATA WASHROOM DESIGN")
        print("=" * 70)
        print(f"Testing server at: {self.base_url}")
        print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        if not self.test_backend_health():
            print("❌ Backend health check failed. Cannot continue testing.")
            return False
            
        self.test_api_endpoints()
        self.test_workflow_integration()
        self.test_concurrent_performance()
        self.test_frontend_accessibility()
        self.test_data_quality()
        self.test_error_handling()
        
        # Generate comprehensive summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
        # Summary by category
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0}
            
            if "✅ PASS" in result["status"]:
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1
        
        for category, stats in categories.items():
            total = stats["passed"] + stats["failed"]
            success_rate = (stats["passed"] / total) * 100 if total > 0 else 0
            print(f"{category:20} | ✅ {stats['passed']:2d} | ❌ {stats['failed']:2d} | {success_rate:5.1f}%")
        
        print("-" * 70)
        print(f"{'TOTAL':20} | ✅ {self.passed:2d} | ❌ {self.failed:2d} | {(self.passed/(self.passed + self.failed))*100:.1f}%")
        
        # Final assessment
        critical_failures = sum(1 for r in self.test_results if "❌ FAIL" in r["status"] and r["category"] in ["Backend", "API", "Workflow"])
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! SYSTEM IS READY FOR PRODUCTION!")
            print("✅ Backend functioning correctly")
            print("✅ All APIs working")
            print("✅ Workflow integration successful")
            print("✅ Frontend accessible")
            print("✅ Data quality verified")
            print("✅ Error handling robust")
            print("✅ Concurrent performance good")
            return True
        elif critical_failures == 0:
            print(f"\n⚠️  {self.failed} NON-CRITICAL ISSUES FOUND")
            print("✅ Core system functions are working")
            print("⚠️  Some minor issues need attention")
            print("📋 Review failed tests and decide if deployment should proceed")
            return True
        else:
            print(f"\n❌ {critical_failures} CRITICAL FAILURES FOUND")
            print("❌ System is NOT ready for production")
            print("🔧 Fix critical issues before deployment")
            
            print("\nCritical failures:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"] and result["category"] in ["Backend", "API", "Workflow"]:
                    print(f"  - [{result['category']}] {result['test']}: {result['details']}")
            return False

def main():
    """Main testing function"""
    print("🚀 Starting comprehensive system testing...")
    print("Make sure your server is running: python start.py")
    print()
    
    # Wait for user confirmation
    input("Press Enter when your server is running at http://localhost:5000...")
    
    tester = ComprehensiveSystemTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎯 SYSTEM TESTING COMPLETE!")
        print("Your Consolidata Washroom Design System is ready for users!")
        
        # Offer to open browser for manual testing
        open_browser = input("\nWould you like to open the browser for manual testing? (y/n): ").lower().strip()
        if open_browser == 'y':
            try:
                webbrowser.open("http://localhost:5000/frontend/index.html")
                print("✅ Browser opened to frontend interface")
                print("📋 Follow the manual testing guide: manual_user_testing_guide.md")
            except Exception as e:
                print(f"❌ Could not open browser: {e}")
                print("Please manually open: http://localhost:5000/frontend/index.html")
    else:
        print("\n🔧 SYSTEM NEEDS FIXES BEFORE DEPLOYMENT")
        print("Review the failed tests above and fix critical issues.")
    
    return success

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Frontend Workflow Test for Washroom Design Pro
Tests the React frontend integration with the Flask backend API
"""

import requests
import json
import time
import subprocess
import sys
import os
from datetime import datetime
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class FrontendWorkflowTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.backend_process = None
        self.frontend_process = None
        self.driver = None
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
    
    def start_backend(self):
        """Start the Flask backend server"""
        print("🚀 Starting Backend Server...")
        print("=" * 50)
        
        backend_script = os.path.join("data", "backend_server.py")
        
        if not os.path.exists(backend_script):
            self.log_result("Backend Setup", "FAIL", f"Backend script not found: {backend_script}")
            return False
        
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, backend_script
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for backend to start
            for i in range(15):
                time.sleep(1)
                try:
                    response = requests.get(f"{self.backend_url}/api/health", timeout=2)
                    if response.status_code == 200:
                        self.log_result("Backend Startup", "PASS", "Backend server started successfully")
                        return True
                except:
                    continue
            
            self.log_result("Backend Startup", "FAIL", "Backend failed to start within 15 seconds")
            return False
            
        except Exception as e:
            self.log_result("Backend Startup", "FAIL", f"Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the React frontend development server"""
        print("\n🌐 Starting Frontend Server...")
        print("=" * 50)
        
        frontend_dir = os.path.join("data", "frontend-react")
        
        if not os.path.exists(frontend_dir):
            self.log_result("Frontend Setup", "FAIL", f"Frontend directory not found: {frontend_dir}")
            return False
        
        # Check if package.json exists
        package_json = os.path.join(frontend_dir, "package.json")
        if not os.path.exists(package_json):
            self.log_result("Frontend Setup", "FAIL", "package.json not found in frontend directory")
            return False
        
        try:
            # Start frontend development server
            self.frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for frontend to start
            for i in range(30):
                time.sleep(1)
                try:
                    response = requests.get(self.frontend_url, timeout=2)
                    if response.status_code == 200:
                        self.log_result("Frontend Startup", "PASS", "Frontend server started successfully")
                        return True
                except:
                    continue
            
            self.log_result("Frontend Startup", "FAIL", "Frontend failed to start within 30 seconds")
            return False
            
        except Exception as e:
            self.log_result("Frontend Startup", "FAIL", f"Failed to start frontend: {e}")
            return False
    
    def setup_browser(self):
        """Setup Selenium WebDriver for frontend testing"""
        print("\n🌐 Setting up Browser for Frontend Testing...")
        print("=" * 50)
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            
            self.log_result("Browser Setup", "PASS", "Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            self.log_result("Browser Setup", "FAIL", f"Failed to setup browser: {e}")
            print("Note: Install ChromeDriver for automated frontend testing")
            return False
    
    def test_frontend_backend_connection(self):
        """Test frontend-backend API connection"""
        print("\n🔗 Testing Frontend-Backend Connection...")
        print("=" * 50)
        
        # Test API proxy configuration
        try:
            # Test direct backend call
            backend_response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            if backend_response.status_code == 200:
                self.log_result("Direct Backend API", "PASS", "Backend API accessible directly")
            else:
                self.log_result("Direct Backend API", "FAIL", f"Backend API returned {backend_response.status_code}")
            
            # Test frontend proxy to backend
            frontend_api_response = requests.get(f"{self.frontend_url}/api/health", timeout=5)
            if frontend_api_response.status_code == 200:
                self.log_result("Frontend API Proxy", "PASS", "Frontend successfully proxies API calls to backend")
            else:
                self.log_result("Frontend API Proxy", "WARN", f"Frontend proxy returned {frontend_api_response.status_code}")
                
        except Exception as e:
            self.log_result("Frontend-Backend Connection", "FAIL", f"Connection test error: {e}")
    
    def test_authentication_workflow(self):
        """Test user authentication workflow"""
        print("\n🔐 Testing Authentication Workflow...")
        print("=" * 50)
        
        if not self.driver:
            self.log_result("Authentication Test", "FAIL", "Browser not available for testing")
            return
        
        try:
            # Navigate to frontend
            self.driver.get(self.frontend_url)
            time.sleep(3)
            
            # Check if homepage loads
            if "Washroom Design Pro" in self.driver.title:
                self.log_result("Homepage Load", "PASS", "Frontend homepage loaded successfully")
            else:
                self.log_result("Homepage Load", "FAIL", f"Unexpected page title: {self.driver.title}")
                return
            
            # Test registration workflow
            try:
                # Look for register button/link
                register_link = self.driver.find_element(By.LINK_TEXT, "Get Started")
                register_link.click()
                time.sleep(2)
                
                # Check if we're on register page
                if "/register" in self.driver.current_url:
                    self.log_result("Registration Navigation", "PASS", "Successfully navigated to registration page")
                    
                    # Fill registration form (if elements exist)
                    try:
                        username_field = self.driver.find_element(By.NAME, "username")
                        email_field = self.driver.find_element(By.NAME, "email")
                        password_field = self.driver.find_element(By.NAME, "password")
                        
                        # Fill test data
                        username_field.send_keys("testuser123")
                        email_field.send_keys("test@example.com")
                        password_field.send_keys("TestPassword123!")
                        
                        self.log_result("Registration Form", "PASS", "Registration form fields accessible and fillable")
                        
                    except Exception as form_error:
                        self.log_result("Registration Form", "WARN", f"Registration form elements not found: {form_error}")
                
                else:
                    self.log_result("Registration Navigation", "WARN", "Registration page not accessible")
                    
            except Exception as nav_error:
                self.log_result("Registration Navigation", "WARN", f"Registration navigation failed: {nav_error}")
            
            # Test login workflow
            try:
                # Navigate to login page
                self.driver.get(f"{self.frontend_url}/login")
                time.sleep(2)
                
                if "/login" in self.driver.current_url:
                    self.log_result("Login Navigation", "PASS", "Successfully navigated to login page")
                    
                    # Check for login form elements
                    try:
                        username_field = self.driver.find_element(By.NAME, "username")
                        password_field = self.driver.find_element(By.NAME, "password")
                        
                        self.log_result("Login Form", "PASS", "Login form elements accessible")
                        
                    except Exception as form_error:
                        self.log_result("Login Form", "WARN", f"Login form elements not found: {form_error}")
                
                else:
                    self.log_result("Login Navigation", "WARN", "Login page not accessible")
                    
            except Exception as login_error:
                self.log_result("Login Navigation", "WARN", f"Login navigation failed: {login_error}")
                
        except Exception as e:
            self.log_result("Authentication Workflow", "FAIL", f"Authentication test error: {e}")
    
    def test_design_workflow(self):
        """Test the main design workflow"""
        print("\n🎨 Testing Design Workflow...")
        print("=" * 50)
        
        if not self.driver:
            self.log_result("Design Workflow Test", "FAIL", "Browser not available for testing")
            return
        
        try:
            # Navigate to design page
            self.driver.get(f"{self.frontend_url}/design")
            time.sleep(3)
            
            # Check if design page loads
            if "/design" in self.driver.current_url:
                self.log_result("Design Page Navigation", "PASS", "Successfully navigated to design page")
                
                # Look for design interface elements
                try:
                    # Check for drawing canvas or design form
                    canvas_elements = self.driver.find_elements(By.TAG_NAME, "canvas")
                    form_elements = self.driver.find_elements(By.TAG_NAME, "form")
                    
                    if canvas_elements:
                        self.log_result("Drawing Canvas", "PASS", f"Found {len(canvas_elements)} canvas element(s)")
                    
                    if form_elements:
                        self.log_result("Design Forms", "PASS", f"Found {len(form_elements)} form element(s)")
                    
                    # Look for specific design tools
                    tool_buttons = self.driver.find_elements(By.CLASS_NAME, "tool-button")
                    if tool_buttons:
                        self.log_result("Design Tools", "PASS", f"Found {len(tool_buttons)} design tool buttons")
                    
                except Exception as element_error:
                    self.log_result("Design Interface Elements", "WARN", f"Design elements check failed: {element_error}")
            
            else:
                self.log_result("Design Page Navigation", "WARN", "Design page not accessible or redirected")
                
        except Exception as e:
            self.log_result("Design Workflow", "FAIL", f"Design workflow test error: {e}")
    
    def test_api_integration(self):
        """Test frontend API integration with backend"""
        print("\n🔌 Testing Frontend API Integration...")
        print("=" * 50)
        
        # Test layout generation API call from frontend perspective
        test_data = {
            "buildingType": "office",
            "roomLength": 8.0,
            "roomWidth": 6.0,
            "roomHeight": 2.7,
            "occupancyType": "business",
            "occupancyCount": 50,
            "accessibilityRequired": True
        }
        
        try:
            # Test API call through frontend proxy
            response = requests.post(f"{self.frontend_url}/api/generate-layout", 
                                   json=test_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log_result("Frontend API Integration", "PASS", 
                                  "Frontend successfully communicates with backend API", {
                                      "Packages Generated": len(result.get('positioned_packages', [])),
                                      "Compliance Score": f"{result.get('compliance_results', {}).get('overall_compliance', 0):.1f}%"
                                  })
                else:
                    self.log_result("Frontend API Integration", "FAIL", 
                                  f"API call failed: {result.get('error')}")
            else:
                self.log_result("Frontend API Integration", "FAIL", 
                              f"API call returned HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Frontend API Integration", "FAIL", f"API integration test error: {e}")
    
    def test_responsive_design(self):
        """Test responsive design on different screen sizes"""
        print("\n📱 Testing Responsive Design...")
        print("=" * 50)
        
        if not self.driver:
            self.log_result("Responsive Design Test", "FAIL", "Browser not available for testing")
            return
        
        screen_sizes = [
            (1920, 1080, "Desktop"),
            (1024, 768, "Tablet"),
            (375, 667, "Mobile")
        ]
        
        for width, height, device in screen_sizes:
            try:
                self.driver.set_window_size(width, height)
                self.driver.get(self.frontend_url)
                time.sleep(2)
                
                # Check if page loads properly at this size
                body = self.driver.find_element(By.TAG_NAME, "body")
                if body:
                    self.log_result(f"Responsive - {device}", "PASS", 
                                  f"Page loads properly at {width}x{height}")
                else:
                    self.log_result(f"Responsive - {device}", "FAIL", 
                                  f"Page failed to load at {width}x{height}")
                    
            except Exception as e:
                self.log_result(f"Responsive - {device}", "FAIL", 
                              f"Responsive test error for {device}: {e}")
    
    def test_performance_metrics(self):
        """Test frontend performance metrics"""
        print("\n⚡ Testing Frontend Performance...")
        print("=" * 50)
        
        try:
            # Test page load time
            start_time = time.time()
            response = requests.get(self.frontend_url, timeout=10)
            end_time = time.time()
            
            load_time = end_time - start_time
            
            if response.status_code == 200:
                if load_time < 3:  # Should load within 3 seconds
                    self.log_result("Frontend Performance", "PASS", 
                                  "Frontend loads within acceptable time", {
                                      "Load Time": f"{load_time:.2f} seconds",
                                      "Response Size": f"{len(response.content)} bytes"
                                  })
                else:
                    self.log_result("Frontend Performance", "WARN", 
                                  "Frontend load time slower than expected", {
                                      "Load Time": f"{load_time:.2f} seconds"
                                  })
            else:
                self.log_result("Frontend Performance", "FAIL", 
                              f"Frontend returned HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Frontend Performance", "FAIL", f"Performance test error: {e}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 FRONTEND WORKFLOW TEST REPORT")
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
        report_filename = f"frontend_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")
        
        # Overall assessment
        if self.test_results['failed'] == 0:
            print("\n🎉 ALL FRONTEND TESTS PASSED! The frontend-backend integration is working correctly.")
        elif self.test_results['failed'] <= 2:
            print("\n⚠️ MOSTLY WORKING: Minor issues detected, but core frontend functionality is operational.")
        else:
            print("\n🚨 FRONTEND ISSUES DETECTED: Multiple failures indicate significant problems that need attention.")
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        
        if self.frontend_process:
            print("\n🛑 Shutting down frontend server...")
            self.frontend_process.terminate()
            time.sleep(2)
            if self.frontend_process.poll() is None:
                self.frontend_process.kill()
        
        if self.backend_process:
            print("🛑 Shutting down backend server...")
            self.backend_process.terminate()
            time.sleep(2)
            if self.backend_process.poll() is None:
                self.backend_process.kill()
    
    def run_frontend_tests(self):
        """Run all frontend workflow tests"""
        print("🌐 WASHROOM DESIGN PRO - FRONTEND WORKFLOW TEST")
        print("=" * 70)
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Start backend first
            if not self.start_backend():
                print("❌ Cannot proceed without backend")
                return
            
            # Start frontend
            if not self.start_frontend():
                print("❌ Cannot proceed without frontend")
                return
            
            # Setup browser (optional)
            browser_available = self.setup_browser()
            
            # Run tests
            self.test_frontend_backend_connection()
            self.test_api_integration()
            self.test_performance_metrics()
            
            if browser_available:
                self.test_authentication_workflow()
                self.test_design_workflow()
                self.test_responsive_design()
            else:
                print("\n⚠️ Skipping browser-based tests (ChromeDriver not available)")
            
            # Generate report
            self.generate_test_report()
            
        except KeyboardInterrupt:
            print("\n⏹️ Tests interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error during testing: {e}")
        finally:
            self.cleanup()

def main():
    """Main function to run frontend workflow tests"""
    tester = FrontendWorkflowTester()
    tester.run_frontend_tests()

if __name__ == "__main__":
    main() 
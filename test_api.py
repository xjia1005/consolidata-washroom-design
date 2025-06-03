#!/usr/bin/env python3
"""
Simple API Test Script
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5000"
    
    print("🔬 Testing Public Washroom Design API")
    print("=" * 50)
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Service: {response.json().get('service', 'Unknown')}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test 2: Basic Analysis
    print("\n🔄 Testing Basic Analysis...")
    try:
        data = {
            "building_type": "office",
            "jurisdiction": "NBC",
            "occupancy_load": 150,
            "room_dimensions": {"length": 12.0, "width": 8.0, "height": 3.0},
            "accessibility_level": "enhanced"
        }
        response = requests.post(f"{base_url}/api/complete-analysis", json=data, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success', False)}")
            if 'report' in result:
                report = result['report']
                fixtures = report.get('fixture_requirements', {})
                print(f"   Fixtures: {fixtures.get('total_fixtures', 0)} total")
                print(f"   Compliance Score: {report.get('compliance_score', 0):.1f}%")
        else:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Basic Analysis Failed: {e}")
    
    # Test 3: Enhanced Analysis
    print("\n🎯 Testing Enhanced Analysis...")
    try:
        data = {
            "building_type": "office",
            "jurisdiction": "NBC",
            "occupancy_load": 150,
            "room_length": 12.0,
            "room_width": 8.0,
            "accessibility_level": "enhanced"
        }
        response = requests.post(f"{base_url}/api/enhanced-analysis", json=data, timeout=15)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Workflow ID: {result.get('workflow_id', 'N/A')}")
            if 'final_results' in result:
                final = result['final_results']
                print(f"   Traceability Complete: {final.get('traceability_complete', False)}")
                if 'compliance_checklist' in final:
                    checklist = final['compliance_checklist']
                    print(f"   Checklist Sections: {len(checklist.get('sections', []))}")
        else:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Enhanced Analysis Failed: {e}")
    
    print("\n📊 Test Summary Complete")

if __name__ == "__main__":
    test_api() 
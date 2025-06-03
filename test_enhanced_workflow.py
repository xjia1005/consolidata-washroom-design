#!/usr/bin/env python3
"""
🎯 Test Script for Enhanced High-Accuracy Building Code Workflow
Demonstrates complete traceability and clause coverage
"""

import requests
import json
import time
from datetime import datetime

# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "Office Building - Basic Scenario",
        "description": "Standard office building with 150 occupants",
        "data": {
            "building_type": "office",
            "jurisdiction": "NBC",
            "occupancy_load": 150,
            "room_length": 12.0,
            "room_width": 8.0,
            "room_height": 3.0,
            "accessibility_level": "enhanced",
            "special_requirements": []
        }
    },
    {
        "name": "Daycare Facility - Child-Specific Requirements",
        "description": "Daycare facility requiring child-height fixtures",
        "data": {
            "building_type": "daycare",
            "jurisdiction": "NBC",
            "occupancy_load": 35,
            "room_length": 10.0,
            "room_width": 6.0,
            "room_height": 3.0,
            "accessibility_level": "enhanced",
            "special_requirements": ["child_facilities"]
        }
    },
    {
        "name": "Alberta Office - Enhanced Accessibility",
        "description": "Alberta office with enhanced accessibility requirements",
        "data": {
            "building_type": "office",
            "jurisdiction": "Alberta",
            "occupancy_load": 200,
            "room_length": 15.0,
            "room_width": 10.0,
            "room_height": 3.0,
            "accessibility_level": "enhanced",
            "special_requirements": ["family_facilities"]
        }
    },
    {
        "name": "School Building - Mixed Age Requirements",
        "description": "School requiring both adult and child fixtures",
        "data": {
            "building_type": "school",
            "jurisdiction": "NBC",
            "occupancy_load": 300,
            "room_length": 20.0,
            "room_width": 12.0,
            "room_height": 3.5,
            "accessibility_level": "enhanced",
            "special_requirements": ["child_facilities", "family_facilities"]
        }
    }
]

def test_enhanced_workflow():
    """Test the enhanced workflow with multiple scenarios"""
    
    print("🎯 Testing Enhanced High-Accuracy Building Code Workflow")
    print("=" * 70)
    
    base_url = "http://localhost:5000"
    
    # Test API health first
    try:
        health_response = requests.get(f"{base_url}/api/health")
        if health_response.status_code != 200:
            print("❌ API is not running. Please start the server first.")
            return
        print("✅ API is running")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please start the server first.")
        return
    
    print()
    
    # Test each scenario
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"🔄 Test {i}: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        print("-" * 50)
        
        try:
            # Send request to enhanced analysis endpoint
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/enhanced-analysis",
                json=scenario["data"],
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ Analysis completed successfully")
                print(f"⏱️  Processing time: {end_time - start_time:.2f} seconds")
                print(f"🆔 Workflow ID: {result['workflow_id']}")
                print()
                
                # Display workflow steps
                print("📋 Workflow Steps:")
                for step_key, step_data in result["workflow_steps"].items():
                    status_icon = "✅" if step_data["status"] == "completed" else "❌"
                    print(f"  {status_icon} {step_data['name']}")
                    
                    # Show step-specific metrics
                    summary = step_data.get("summary", {})
                    if summary.get("rules_found"):
                        print(f"      📏 Rules found: {summary['rules_found']}")
                    if summary.get("components_required"):
                        print(f"      🔧 Components required: {summary['components_required']}")
                    if summary.get("clauses_found"):
                        print(f"      📜 Clauses found: {summary['clauses_found']}")
                    if summary.get("coverage_score"):
                        print(f"      📊 Coverage score: {summary['coverage_score']:.1f}%")
                
                print()
                
                # Display summary metrics
                summary = result["summary"]
                print("📊 Summary Metrics:")
                print(f"  📋 Total checklist items: {summary['total_checklist_items']}")
                print(f"  🚨 Critical items: {summary['critical_items']}")
                print(f"  📈 Coverage percentage: {summary['coverage_percentage']:.1f}%")
                print(f"  🏗️  Layout efficiency: {summary['layout_efficiency']:.1f}%")
                print(f"  ✅ Compliance score: {summary['compliance_score']:.1f}%")
                print()
                
                # Display validation status
                validation = result["validation_summary"]
                print("🔍 Validation Status:")
                print(f"  ✅ Complete: {validation['is_complete']}")
                print(f"  ⚠️  Warnings: {len(validation['warnings'])}")
                print(f"  ❌ Errors: {len(validation['errors'])}")
                
                if validation["warnings"]:
                    print("  ⚠️  Warning details:")
                    for warning in validation["warnings"]:
                        print(f"    - {warning['message']} (Severity: {warning['severity']})")
                
                if validation["errors"]:
                    print("  ❌ Error details:")
                    for error in validation["errors"]:
                        print(f"    - {error['message']} (Severity: {error['severity']})")
                
                print()
                
                # Display sample checklist items
                checklist = result["compliance_checklist"]
                print("📋 Sample Compliance Checklist Items:")
                
                for section in checklist["sections"][:2]:  # Show first 2 sections
                    print(f"  {section['icon']} {section['title']} ({section['total_items']} items)")
                    
                    for item in section["items"][:3]:  # Show first 3 items per section
                        priority_icon = "🚨" if item["priority"] == "critical" else "⚠️" if item["priority"] == "important" else "ℹ️"
                        print(f"    {priority_icon} {item['title']}")
                        print(f"      📖 {item['code_reference']}")
                        print(f"      🔍 Verification: {item['verification_method']}")
                        if item["affected_components"]:
                            print(f"      🔧 Components: {', '.join(item['affected_components'][:2])}")
                        print()
                
                # Display layout information
                layout = result["layout_design"]
                print("🏗️  Layout Design:")
                print(f"  📐 Room: {layout['room_dimensions']['length']}m × {layout['room_dimensions']['width']}m")
                print(f"  🔧 Assemblies positioned: {len(layout['positioned_assemblies'])}")
                
                for assembly in layout["positioned_assemblies"][:3]:  # Show first 3 assemblies
                    pos = assembly["position"]
                    print(f"    - {assembly['assembly_name']}: ({pos['x']:.1f}, {pos['y']:.1f}) - {pos['width']:.1f}×{pos['height']:.1f}m")
                
                print()
                
            else:
                print(f"❌ Analysis failed with status code: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("=" * 70)
        print()

def test_comparison_with_basic_analysis():
    """Compare enhanced analysis with basic analysis"""
    
    print("🔄 Comparing Enhanced vs Basic Analysis")
    print("=" * 50)
    
    test_data = {
        "building_type": "office",
        "jurisdiction": "NBC",
        "occupancy_load": 150,
        "room_length": 12.0,
        "room_width": 8.0,
        "room_height": 3.0,
        "accessibility_level": "enhanced"
    }
    
    base_url = "http://localhost:5000"
    
    try:
        # Test basic analysis
        print("🔄 Running basic analysis...")
        basic_response = requests.post(
            f"{base_url}/api/complete-analysis",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Test enhanced analysis
        print("🔄 Running enhanced analysis...")
        enhanced_response = requests.post(
            f"{base_url}/api/enhanced-analysis",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if basic_response.status_code == 200 and enhanced_response.status_code == 200:
            basic_result = basic_response.json()
            enhanced_result = enhanced_response.json()
            
            print("📊 Comparison Results:")
            print(f"  Basic Analysis:")
            print(f"    - Checklist items: {len(basic_result.get('compliance_checklist', {}).get('items', []))}")
            print(f"    - Layout components: {len(basic_result.get('layout', {}).get('components', []))}")
            
            print(f"  Enhanced Analysis:")
            print(f"    - Checklist items: {enhanced_result['summary']['total_checklist_items']}")
            print(f"    - Critical items: {enhanced_result['summary']['critical_items']}")
            print(f"    - Coverage score: {enhanced_result['summary']['coverage_percentage']:.1f}%")
            print(f"    - Traceability: {'Complete' if enhanced_result['traceability_complete'] else 'Incomplete'}")
            
            print("\n✅ Enhanced analysis provides:")
            print("  - Complete clause traceability")
            print("  - Component-level validation")
            print("  - Multi-step workflow verification")
            print("  - Detailed compliance scoring")
            
        else:
            print("❌ One or both analyses failed")
            
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")

if __name__ == "__main__":
    print("🎯 Enhanced Building Code Workflow Test Suite")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run main workflow tests
    test_enhanced_workflow()
    
    # Run comparison test
    test_comparison_with_basic_analysis()
    
    print("🎯 Test suite completed!")
    print(f"🕐 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 
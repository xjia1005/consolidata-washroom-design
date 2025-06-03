#!/usr/bin/env python3
"""
Test script to verify SQLite threading fix
Tests concurrent requests to ensure no threading errors
"""

import requests
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_enhanced_analysis(thread_id):
    """Test the enhanced analysis endpoint"""
    try:
        response = requests.post(
            'http://localhost:5000/api/enhanced-analysis',
            json={
                'building_type': 'office',
                'jurisdiction': 'NBC',
                'occupancy_load': 150,
                'room_length': 12.0,
                'room_width': 8.0,
                'accessibility_level': 'enhanced'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'thread_id': thread_id,
                'status': 'SUCCESS',
                'status_code': response.status_code,
                'workflow_id': data.get('workflow_id', 'N/A'),
                'checklist_items': data.get('summary', {}).get('total_checklist_items', 0)
            }
        else:
            return {
                'thread_id': thread_id,
                'status': 'FAILED',
                'status_code': response.status_code,
                'error': response.text[:200]
            }
            
    except Exception as e:
        return {
            'thread_id': thread_id,
            'status': 'ERROR',
            'error': str(e)
        }

def test_basic_analysis(thread_id):
    """Test the basic analysis endpoint"""
    try:
        response = requests.post(
            'http://localhost:5000/api/complete-analysis',
            json={
                'building_type': 'office',
                'jurisdiction': 'NBC',
                'occupancy_load': 100,
                'accessibility_level': 'basic',
                'room_dimensions': {'length': 10, 'width': 8, 'height': 3}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'thread_id': thread_id,
                'status': 'SUCCESS',
                'status_code': response.status_code,
                'fixtures': data.get('report', {}).get('fixture_requirements', {}).get('total_fixtures', 0)
            }
        else:
            return {
                'thread_id': thread_id,
                'status': 'FAILED',
                'status_code': response.status_code,
                'error': response.text[:200]
            }
            
    except Exception as e:
        return {
            'thread_id': thread_id,
            'status': 'ERROR',
            'error': str(e)
        }

def main():
    print("🧪 SQLite Threading Fix - Concurrent Test")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Concurrent Enhanced Analysis
    print("\n2️⃣ Testing Concurrent Enhanced Analysis (10 threads)...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit 10 concurrent requests
        futures = [executor.submit(test_enhanced_analysis, i) for i in range(10)]
        
        results = []
        for future in as_completed(futures):
            results.append(future.result())
    
    # Analyze results
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed_count = sum(1 for r in results if r['status'] == 'FAILED')
    error_count = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"   ✅ Successful: {success_count}/10")
    print(f"   ❌ Failed: {failed_count}/10")
    print(f"   🚨 Errors: {error_count}/10")
    
    if error_count > 0:
        print("\n🚨 Error Details:")
        for result in results:
            if result['status'] == 'ERROR':
                print(f"   Thread {result['thread_id']}: {result['error']}")
    
    # Test 3: Concurrent Basic Analysis
    print("\n3️⃣ Testing Concurrent Basic Analysis (5 threads)...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(test_basic_analysis, i) for i in range(5)]
        
        basic_results = []
        for future in as_completed(futures):
            basic_results.append(future.result())
    
    basic_success = sum(1 for r in basic_results if r['status'] == 'SUCCESS')
    print(f"   ✅ Successful: {basic_success}/5")
    
    # Test 4: Mixed Load Test
    print("\n4️⃣ Testing Mixed Load (Enhanced + Basic simultaneously)...")
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Mix of enhanced and basic requests
        mixed_futures = []
        for i in range(4):
            mixed_futures.append(executor.submit(test_enhanced_analysis, f"enhanced_{i}"))
            mixed_futures.append(executor.submit(test_basic_analysis, f"basic_{i}"))
        
        mixed_results = []
        for future in as_completed(mixed_futures):
            mixed_results.append(future.result())
    
    mixed_success = sum(1 for r in mixed_results if r['status'] == 'SUCCESS')
    print(f"   ✅ Successful: {mixed_success}/8")
    
    # Final Summary
    print("\n📊 FINAL RESULTS")
    print("=" * 50)
    
    total_tests = len(results) + len(basic_results) + len(mixed_results)
    total_success = success_count + basic_success + mixed_success
    
    print(f"Total Tests: {total_tests}")
    print(f"Total Successful: {total_success}")
    print(f"Success Rate: {(total_success/total_tests)*100:.1f}%")
    
    if total_success == total_tests:
        print("\n🎉 ALL TESTS PASSED! SQLite threading fix is working perfectly!")
        print("✅ Your system is now production-ready for concurrent users!")
    else:
        print(f"\n⚠️  {total_tests - total_success} tests failed. Check the errors above.")
    
    print("\n🚀 Next Steps:")
    print("1. Deploy to production environment")
    print("2. Set up monitoring and logging")
    print("3. Test with real user load")
    print("4. Monitor performance metrics")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script to test all API endpoints and report errors.
"""
import requests
import json
import sys
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, data: dict = None, expected_status: int = 200) -> Tuple[bool, Dict]:
    """Test an endpoint and return success status and response."""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return False, {"error": f"Unsupported method: {method}"}
        
        success = response.status_code == expected_status
        try:
            response_data = response.json()
        except:
            response_data = {"raw": response.text}
        
        return success, {
            "status_code": response.status_code,
            "expected": expected_status,
            "data": response_data
        }
    except requests.exceptions.ConnectionError:
        return False, {"error": "Connection refused - server not running"}
    except Exception as e:
        return False, {"error": str(e)}

def main():
    print("=" * 60)
    print("Testing API Endpoints")
    print("=" * 60)
    print()
    
    errors = []
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Root endpoint
    print("1. Testing GET /")
    success, result = test_endpoint("GET", "/")
    if success:
        print(f"   ✅ PASSED - Status: {result['status_code']}")
        tests_passed += 1
    else:
        print(f"   ❌ FAILED - {result}")
        errors.append(("GET /", result))
        tests_failed += 1
    print()
    
    # Test 2: Health check
    print("2. Testing GET /health")
    success, result = test_endpoint("GET", "/health")
    if success:
        print(f"   ✅ PASSED - Status: {result['status_code']}")
        print(f"   Response: {json.dumps(result['data'], indent=6)}")
        tests_passed += 1
    else:
        print(f"   ❌ FAILED - {result}")
        errors.append(("GET /health", result))
        tests_failed += 1
    print()
    
    # Test 3: Health ready
    print("3. Testing GET /health/ready")
    success, result = test_endpoint("GET", "/health/ready")
    if success:
        print(f"   ✅ PASSED - Status: {result['status_code']}")
        tests_passed += 1
    else:
        print(f"   ❌ FAILED - {result}")
        errors.append(("GET /health/ready", result))
        tests_failed += 1
    print()
    
    # Test 4: Health live
    print("4. Testing GET /health/live")
    success, result = test_endpoint("GET", "/health/live")
    if success:
        print(f"   ✅ PASSED - Status: {result['status_code']}")
        tests_passed += 1
    else:
        print(f"   ❌ FAILED - {result}")
        errors.append(("GET /health/live", result))
        tests_failed += 1
    print()
    
    # Test 5: List pathologies
    print("5. Testing GET /chats/pathologies/list")
    success, result = test_endpoint("GET", "/chats/pathologies/list")
    if success:
        print(f"   ✅ PASSED - Status: {result['status_code']}")
        pathologies = result['data'].get('pathologies', [])
        print(f"   Found {len(pathologies)} pathologies")
        tests_passed += 1
    else:
        print(f"   ❌ FAILED - {result}")
        errors.append(("GET /chats/pathologies/list", result))
        tests_failed += 1
    print()
    
    # Test 6: List chats (should be empty initially)
    print("6. Testing GET /chats")
    success, result = test_endpoint("GET", "/chats")
    if success:
        print(f"   ✅ PASSED - Status: {result['status_code']}")
        tests_passed += 1
    else:
        print(f"   ❌ FAILED - {result}")
        errors.append(("GET /chats", result))
        tests_failed += 1
    print()
    
    # Test 7: Create chat (no pathology)
    print("7. Testing POST /chats (no pathology)")
    success, result = test_endpoint("POST", "/chats", data={}, expected_status=201)
    chat_id = None
    if success:
        print(f"   ✅ PASSED - Status: {result['status_code']}")
        chat_id = result['data'].get('chat_id')
        print(f"   Created chat_id: {chat_id}")
        tests_passed += 1
    else:
        print(f"   ❌ FAILED - {result}")
        errors.append(("POST /chats", result))
        tests_failed += 1
    print()
    
    # Test 8: Get chat details
    if chat_id:
        print(f"8. Testing GET /chats/{chat_id}")
        success, result = test_endpoint("GET", f"/chats/{chat_id}")
        if success:
            print(f"   ✅ PASSED - Status: {result['status_code']}")
            tests_passed += 1
        else:
            print(f"   ❌ FAILED - {result}")
            errors.append((f"GET /chats/{chat_id}", result))
            tests_failed += 1
        print()
        
        # Test 9: Send message
        print(f"9. Testing POST /chats/{chat_id}/message")
        success, result = test_endpoint(
            "POST", 
            f"/chats/{chat_id}/message",
            data={"message": "Hello, how are you feeling today?", "max_new_tokens": 50, "temperature": 0.4},
            expected_status=200
        )
        if success:
            print(f"   ✅ PASSED - Status: {result['status_code']}")
            reply = result['data'].get('reply', '')
            print(f"   Patient response: {reply[:100]}...")
            tests_passed += 1
        else:
            print(f"   ❌ FAILED - {result}")
            errors.append((f"POST /chats/{chat_id}/message", result))
            tests_failed += 1
        print()
        
        # Test 10: Reset chat
        print(f"10. Testing POST /chats/{chat_id}/reset")
        success, result = test_endpoint("POST", f"/chats/{chat_id}/reset")
        if success:
            print(f"   ✅ PASSED - Status: {result['status_code']}")
            tests_passed += 1
        else:
            print(f"   ❌ FAILED - {result}")
            errors.append((f"POST /chats/{chat_id}/reset", result))
            tests_failed += 1
        print()
        
        # Test 11: Delete chat
        print(f"11. Testing DELETE /chats/{chat_id}")
        success, result = test_endpoint("DELETE", f"/chats/{chat_id}", expected_status=204)
        if success:
            print(f"   ✅ PASSED - Status: {result['status_code']}")
            tests_passed += 1
        else:
            print(f"   ❌ FAILED - {result}")
            errors.append((f"DELETE /chats/{chat_id}", result))
            tests_failed += 1
        print()
    
    # Test 12: Invalid chat ID
    print("12. Testing GET /chats/invalid-id (should return 404)")
    success, result = test_endpoint("GET", "/chats/invalid-id", expected_status=404)
    if not success and result.get('status_code') == 404:
        print(f"   ✅ PASSED - Correctly returned 404")
        tests_passed += 1
    else:
        print(f"   ❌ FAILED - Expected 404, got {result}")
        errors.append(("GET /chats/invalid-id", result))
        tests_failed += 1
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    print()
    
    if errors:
        print("ERRORS FOUND:")
        print("-" * 60)
        for endpoint, error in errors:
            print(f"\n{endpoint}:")
            print(json.dumps(error, indent=2))
        return 1
    else:
        print("✅ All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

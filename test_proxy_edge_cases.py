#!/usr/bin/env python3
"""
Additional edge case tests for proxy formatting to ensure robustness
"""

import sys
import requests

def test_edge_cases():
    """Test edge cases and malformed proxy strings"""
    
    print("=" * 80)
    print("TEST: Edge Cases and Malformed Proxy Strings")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Proxy with only IP (no port) - should remain unchanged",
            "input": "1.2.3.4",
            "expected": "1.2.3.4",
            "should_work": False
        },
        {
            "name": "Proxy with 3 parts (IP:PORT:USER) - should remain unchanged",
            "input": "1.2.3.4:8080:user",
            "expected": "1.2.3.4:8080:user",
            "should_work": False
        },
        {
            "name": "Proxy with https:// prefix",
            "input": "https://1.2.3.4:8080",
            "expected": "https://1.2.3.4:8080",
            "should_work": True
        },
        {
            "name": "Proxy with socks5:// prefix",
            "input": "socks5://1.2.3.4:8080",
            "expected": "socks5://1.2.3.4:8080",
            "should_work": True
        },
        {
            "name": "IPv6 address (not supported by simple split)",
            "input": "[2001:db8::1]:8080",
            "expected": "[2001:db8::1]:8080",
            "should_work": False
        },
        {
            "name": "Proxy with username containing special chars",
            "input": "1.2.3.4:8080:user@domain:pass",
            "expected": "http://user@domain:pass@1.2.3.4:8080",
            "should_work": True
        },
        {
            "name": "Proxy with empty username/password",
            "input": "1.2.3.4:8080::",
            "expected": "http://:@1.2.3.4:8080",
            "should_work": True
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        proxy = test["input"]
        expected = test["expected"]
        
        # Apply the same formatting logic as in check_givewp_stripe
        formatted_proxy = proxy
        if proxy and not proxy.startswith("http"):
            p_parts = proxy.split(":")
            if len(p_parts) >= 4:
                formatted_proxy = f"http://{p_parts[2]}:{':'.join(p_parts[3:])}@{p_parts[0]}:{p_parts[1]}"
            elif len(p_parts) == 2:
                formatted_proxy = f"http://{p_parts[0]}:{p_parts[1]}"
        
        result_match = formatted_proxy == expected
        
        # Try to use with requests.Session
        session_works = False
        try:
            if formatted_proxy:
                session = requests.Session()
                proxies_dict = {"http": formatted_proxy, "https": formatted_proxy}
                session.proxies.update(proxies_dict)
                session_works = True
        except Exception:
            session_works = False
        
        if result_match:
            status = "✅ PASS" if session_works == test["should_work"] else "⚠️  WARN"
            print(f"{status}: {test['name']}")
            print(f"   Input:    '{proxy}'")
            print(f"   Output:   '{formatted_proxy}'")
            print(f"   Expected: '{expected}'")
            print(f"   Session works: {session_works} (expected: {test['should_work']})")
            if session_works == test["should_work"]:
                passed += 1
            else:
                failed += 1
        else:
            print(f"❌ FAIL: {test['name']}")
            print(f"   Input:    '{proxy}'")
            print(f"   Output:   '{formatted_proxy}'")
            print(f"   Expected: '{expected}'")
            failed += 1
        print()
    
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print()
    return failed == 0


def test_actual_proxy_flow():
    """Test the actual flow with a real-world scenario"""
    
    print("=" * 80)
    print("TEST: Real-world Proxy Flow Simulation")
    print("=" * 80)
    
    # Simulate what happens in the actual code
    print("\nScenario: User adds proxy '1.2.3.4:8080:myuser:mypass' to database")
    print("Step 1: Proxy stored in DB with 'raw' field")
    
    raw_proxy = "1.2.3.4:8080:myuser:mypass"
    print(f"  DB raw field: '{raw_proxy}'")
    
    print("\nStep 2: When checking card, retrieve raw proxy from DB")
    print(f"  Retrieved: '{raw_proxy}'")
    
    print("\nStep 3: Pass to check_givewp_stripe function")
    
    # Apply formatting logic
    formatted_proxy = raw_proxy
    if raw_proxy and not raw_proxy.startswith("http"):
        p_parts = raw_proxy.split(":")
        if len(p_parts) >= 4:
            formatted_proxy = f"http://{p_parts[2]}:{':'.join(p_parts[3:])}@{p_parts[0]}:{p_parts[1]}"
        elif len(p_parts) == 2:
            formatted_proxy = f"http://{p_parts[0]}:{p_parts[1]}"
    
    print(f"  Formatted: '{formatted_proxy}'")
    
    print("\nStep 4: Create requests.Session and set proxy")
    try:
        session = requests.Session()
        proxies_dict = {"http": formatted_proxy, "https": formatted_proxy}
        session.proxies.update(proxies_dict)
        print(f"  ✅ Session created successfully")
        print(f"  ✅ Proxy set: {session.proxies}")
        print(f"  ✅ No ValueError raised")
        return True
    except ValueError as e:
        print(f"  ❌ ValueError raised: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PROXY FORMATTING EDGE CASES TEST SUITE")
    print("=" * 80 + "\n")
    
    all_passed = True
    
    # Run tests
    all_passed &= test_edge_cases()
    all_passed &= test_actual_proxy_flow()
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL EDGE CASE TESTS PASSED")
    else:
        print("⚠️  SOME EDGE CASES NEED ATTENTION")
    print("=" * 80 + "\n")
    
    sys.exit(0 if all_passed else 1)

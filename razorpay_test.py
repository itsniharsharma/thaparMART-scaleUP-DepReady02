#!/usr/bin/env python3
"""
Direct Razorpay Integration Test
Test the Razorpay credentials and API directly to identify the root cause
"""

import razorpay
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

def test_razorpay_credentials():
    """Test Razorpay credentials directly"""
    print("🔑 Testing Razorpay Credentials...")
    
    try:
        # Get credentials from environment
        key_id = os.environ.get('RAZORPAY_KEY_ID')
        key_secret = os.environ.get('RAZORPAY_KEY_SECRET')
        
        print(f"    📊 Key ID: {key_id}")
        print(f"    📊 Key Secret: {'*' * len(key_secret) if key_secret else 'None'}")
        
        if not key_id or not key_secret:
            print("    ❌ CRITICAL: Razorpay credentials not found in environment!")
            return False
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(key_id, key_secret))
        print("    ✅ Razorpay client initialized successfully")
        
        return client
        
    except Exception as e:
        print(f"    ❌ CRITICAL: Failed to initialize Razorpay client: {str(e)}")
        return False

def test_razorpay_order_creation(client):
    """Test Razorpay order creation with the same parameters as backend"""
    print("\n💳 Testing Razorpay Order Creation...")
    
    if not client:
        print("    ❌ Cannot test - Razorpay client not available")
        return False
    
    try:
        # Use the same parameters as in the backend
        receipt_id = f"fee_test123_{str(uuid.uuid4())[:8]}"
        
        order_data = {
            "amount": 2000,  # 20 Rs in paise
            "currency": "INR",
            "receipt": receipt_id,
            "payment_capture": 1
        }
        
        print(f"    📊 Order Data: {order_data}")
        
        # Create order
        razorpay_order = client.order.create(order_data)
        
        print(f"    ✅ Order created successfully!")
        print(f"    📊 Order ID: {razorpay_order.get('id')}")
        print(f"    📊 Amount: {razorpay_order.get('amount')}")
        print(f"    📊 Currency: {razorpay_order.get('currency')}")
        print(f"    📊 Status: {razorpay_order.get('status')}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ CRITICAL: Failed to create Razorpay order: {str(e)}")
        print(f"    📊 Error Type: {type(e).__name__}")
        
        # Check for specific error types
        if "authentication" in str(e).lower():
            print("    🔍 DIAGNOSIS: Authentication error - check credentials")
        elif "invalid" in str(e).lower():
            print("    🔍 DIAGNOSIS: Invalid parameter error")
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            print("    🔍 DIAGNOSIS: Network connectivity issue")
        else:
            print("    🔍 DIAGNOSIS: Unknown Razorpay API error")
        
        return False

def test_receipt_length_issue():
    """Test if receipt length is causing issues"""
    print("\n📏 Testing Receipt Length Issues...")
    
    client = test_razorpay_credentials()
    if not client:
        return False
    
    # Test different receipt lengths
    test_cases = [
        {"name": "Short Receipt", "receipt": "test123"},
        {"name": "Medium Receipt", "receipt": f"fee_test_{str(uuid.uuid4())[:8]}"},
        {"name": "Long Receipt", "receipt": f"fee_very_long_receipt_id_{str(uuid.uuid4())}"},
        {"name": "Max Length Receipt", "receipt": "a" * 40},  # Razorpay max is 40 chars
        {"name": "Over Max Length", "receipt": "a" * 50}  # This should fail
    ]
    
    for test_case in test_cases:
        try:
            order_data = {
                "amount": 2000,
                "currency": "INR", 
                "receipt": test_case["receipt"],
                "payment_capture": 1
            }
            
            print(f"    📊 Testing {test_case['name']} (length: {len(test_case['receipt'])})")
            
            razorpay_order = client.order.create(order_data)
            print(f"    ✅ {test_case['name']}: SUCCESS")
            
        except Exception as e:
            print(f"    ❌ {test_case['name']}: FAILED - {str(e)}")
            if "receipt" in str(e).lower():
                print(f"    🔍 Receipt length issue confirmed!")

def test_network_connectivity():
    """Test network connectivity to Razorpay"""
    print("\n🌐 Testing Network Connectivity to Razorpay...")
    
    try:
        import requests
        
        # Test connectivity to Razorpay API
        response = requests.get("https://api.razorpay.com", timeout=10)
        print(f"    📊 Razorpay API Status: {response.status_code}")
        
        if response.status_code == 200:
            print("    ✅ Network connectivity to Razorpay is working")
        else:
            print(f"    ⚠️  Unexpected response from Razorpay API: {response.status_code}")
            
    except Exception as e:
        print(f"    ❌ Network connectivity issue: {str(e)}")

def main():
    """Run all Razorpay tests"""
    print("🎯 DIRECT RAZORPAY INTEGRATION TESTING")
    print("=" * 60)
    print("🔍 Investigating root cause of 'Failed to create payment order'")
    print("=" * 60)
    
    # Test network connectivity first
    test_network_connectivity()
    
    # Test credentials
    client = test_razorpay_credentials()
    
    # Test order creation
    if client:
        success = test_razorpay_order_creation(client)
        
        if not success:
            # If order creation failed, test receipt length issues
            test_receipt_length_issue()
    
    print("\n" + "=" * 60)
    print("📊 RAZORPAY TEST SUMMARY")
    print("=" * 60)
    
    if client:
        print("✅ Razorpay credentials are valid")
        print("💡 If order creation failed, check the specific error above")
        print("🔧 Common issues:")
        print("   - Receipt ID too long (max 40 characters)")
        print("   - Invalid amount (must be in paise)")
        print("   - Network connectivity issues")
        print("   - Account not activated for test mode")
    else:
        print("❌ Razorpay credentials are invalid or missing")
        print("🔧 Check backend/.env file for correct credentials")

if __name__ == "__main__":
    main()
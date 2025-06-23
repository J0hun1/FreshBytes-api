#!/usr/bin/env python
"""
Test script to verify that form fields are properly displayed in the browsable API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_form_fields():
    """Test that the form fields are properly displayed"""
    
    print("🧪 Testing Form Fields in Browsable API")
    print("=" * 50)
    
    # Test 1: Check add-products endpoint form
    print("\n1️⃣ Testing add-products endpoint form...")
    try:
        response = requests.get(f"{BASE_URL}/promos/pid00125/add-products/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Add Products Form:")
            print(f"   Promo ID: {data.get('promo_id')}")
            print(f"   Promo Name: {data.get('promo_name')}")
            print(f"   Help Text: {data.get('help_text')}")
            print(f"   Form Fields: {list(data.get('form_fields', {}).keys())}")
        else:
            print(f"❌ Failed to get add-products form: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Check remove-products endpoint form
    print("\n2️⃣ Testing remove-products endpoint form...")
    try:
        response = requests.get(f"{BASE_URL}/promos/pid00125/remove-products/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Remove Products Form:")
            print(f"   Promo ID: {data.get('promo_id')}")
            print(f"   Promo Name: {data.get('promo_name')}")
            print(f"   Help Text: {data.get('help_text')}")
            print(f"   Form Fields: {list(data.get('form_fields', {}).keys())}")
        else:
            print(f"❌ Failed to get remove-products form: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Check clear-products endpoint info
    print("\n3️⃣ Testing clear-products endpoint info...")
    try:
        response = requests.get(f"{BASE_URL}/promos/pid00125/clear-products/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Clear Products Info:")
            print(f"   Promo ID: {data.get('promo_id')}")
            print(f"   Promo Name: {data.get('promo_name')}")
            print(f"   Current Products: {data.get('current_product_count')}")
            print(f"   Warning: {data.get('warning')}")
            print(f"   Help Text: {data.get('help_text')}")
        else:
            print(f"❌ Failed to get clear-products info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Check get-products endpoint
    print("\n4️⃣ Testing get-products endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/promos/pid00125/products/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get Products:")
            print(f"   Promo ID: {data.get('promo_id')}")
            print(f"   Promo Name: {data.get('promo_name')}")
            print(f"   Total Products: {data.get('total_products')}")
        else:
            print(f"❌ Failed to get products: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n🎉 Form field testing completed!")
    print("\n💡 Now when you visit these URLs in your browser, you should see proper form fields instead of just 'content'!")

if __name__ == "__main__":
    test_form_fields() 
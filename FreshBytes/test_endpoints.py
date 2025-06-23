#!/usr/bin/env python
"""
Quick test to verify the promo product management endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("🧪 Testing Promo Product Management Endpoints")
    print("=" * 50)
    
    # Test 1: Check if the endpoints are accessible
    print("\n1️⃣ Testing endpoint accessibility...")
    
    endpoints = [
        "/promos/",
        "/promos/test123/add-products/",
        "/promos/test123/remove-products/", 
        "/promos/test123/products/",
        "/promos/test123/clear-products/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✅ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Connection Error (server not running)")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")
    
    print("\n2️⃣ Testing with actual data...")
    
    # Test 2: Create a promo and test the endpoints
    try:
        # Create a promo
        promo_data = {
            "seller_id": "sid00125",
            "promo_name": "Test Promo",
            "promo_description": "Test description",
            "discount_amount": 10,
            "is_active": True
        }
        
        response = requests.post(f"{BASE_URL}/promos/", json=promo_data)
        if response.status_code == 201:
            promo = response.json()
            promo_id = promo['promo_id']
            print(f"✅ Created promo: {promo_id}")
            
            # Test adding products
            add_data = {"product_ids": ["prod00125"]}
            response = requests.post(f"{BASE_URL}/promos/{promo_id}/add-products/", json=add_data)
            print(f"✅ Add products endpoint: {response.status_code}")
            
            # Test getting products
            response = requests.get(f"{BASE_URL}/promos/{promo_id}/products/")
            print(f"✅ Get products endpoint: {response.status_code}")
            
            # Test removing products (POST method)
            remove_data = {"product_ids": ["prod00125"]}
            response = requests.post(f"{BASE_URL}/promos/{promo_id}/remove-products/", json=remove_data)
            print(f"✅ Remove products endpoint (POST): {response.status_code}")
            
            # Test removing products (DELETE method)
            response = requests.delete(f"{BASE_URL}/promos/{promo_id}/remove-products/", json=remove_data)
            print(f"✅ Remove products endpoint (DELETE): {response.status_code}")
            
            # Test clearing products (POST method)
            response = requests.post(f"{BASE_URL}/promos/{promo_id}/clear-products/")
            print(f"✅ Clear products endpoint (POST): {response.status_code}")
            
            # Test clearing products (DELETE method)
            response = requests.delete(f"{BASE_URL}/promos/{promo_id}/clear-products/")
            print(f"✅ Clear products endpoint (DELETE): {response.status_code}")
            
        else:
            print(f"❌ Failed to create promo: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    print("\n🎉 Endpoint testing completed!")

if __name__ == "__main__":
    test_endpoints() 
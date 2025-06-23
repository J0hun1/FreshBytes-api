#!/usr/bin/env python
"""
Test script to demonstrate the new Promo Product Management API endpoints
"""
import requests
import json

# Base URL for your API
BASE_URL = "http://localhost:8000"

def test_promo_product_management():
    """Test the new promo product management endpoints"""
    
    print("🧪 Testing Promo Product Management API Endpoints")
    print("=" * 50)
    
    # Step 1: Create a promo first
    print("\n1️⃣ Creating a new promo...")
    promo_data = {
        "seller_id": "sid00125",  # Replace with actual seller ID
        "promo_name": "Test Multi-Product Promo",
        "promo_description": "A test promo for multiple products",
        "discount_amount": 10,
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/promos/", json=promo_data)
    if response.status_code == 201:
        promo = response.json()
        promo_id = promo['promo_id']
        print(f"✅ Created promo: {promo_id}")
    else:
        print(f"❌ Failed to create promo: {response.text}")
        return
    
    # Step 2: Add products to the promo
    print(f"\n2️⃣ Adding products to promo {promo_id}...")
    product_ids = ["prod00125", "prod00225"]  # Replace with actual product IDs
    
    add_data = {
        "product_ids": product_ids
    }
    
    response = requests.post(f"{BASE_URL}/promos/{promo_id}/add-products/", json=add_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   Added products: {result['added_products']}")
    else:
        print(f"❌ Failed to add products: {response.text}")
    
    # Step 3: Get all products in the promo
    print(f"\n3️⃣ Getting all products in promo {promo_id}...")
    
    response = requests.get(f"{BASE_URL}/promos/{promo_id}/products/")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['total_products']} products in promo")
        for product in result['products']:
            print(f"   - {product['product_name']} (ID: {product['product_id']})")
    else:
        print(f"❌ Failed to get products: {response.text}")
    
    # Step 4: Remove a product from the promo
    print(f"\n4️⃣ Removing a product from promo {promo_id}...")
    remove_data = {
        "product_ids": ["prod00125"]  # Remove one product
    }
    
    response = requests.post(f"{BASE_URL}/promos/{promo_id}/remove-products/", json=remove_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   Removed products: {result['removed_products']}")
    else:
        print(f"❌ Failed to remove products: {response.text}")
    
    # Step 5: Get updated product list
    print(f"\n5️⃣ Getting updated products in promo {promo_id}...")
    
    response = requests.get(f"{BASE_URL}/promos/{promo_id}/products/")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Now has {result['total_products']} products in promo")
        for product in result['products']:
            print(f"   - {product['product_name']} (ID: {product['product_id']})")
    else:
        print(f"❌ Failed to get products: {response.text}")
    
    # Step 6: Clear all products from the promo
    print(f"\n6️⃣ Clearing all products from promo {promo_id}...")
    
    response = requests.post(f"{BASE_URL}/promos/{promo_id}/clear-products/")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Failed to clear products: {response.text}")
    
    # Step 7: Verify promo is empty
    print(f"\n7️⃣ Verifying promo {promo_id} is empty...")
    
    response = requests.get(f"{BASE_URL}/promos/{promo_id}/products/")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Promo now has {result['total_products']} products")
    else:
        print(f"❌ Failed to get products: {response.text}")
    
    print("\n🎉 All tests completed!")

def show_api_usage():
    """Show how to use the API endpoints"""
    print("\n📚 API Usage Examples:")
    print("=" * 50)
    
    print("""
1. ADD PRODUCTS TO A PROMO:
   POST /promos/{promo_id}/add-products/
   Body: {"product_ids": ["prod00125", "prod00225"]}

2. REMOVE PRODUCTS FROM A PROMO:
   POST /promos/{promo_id}/remove-products/
   Body: {"product_ids": ["prod00125"]}

3. GET ALL PRODUCTS IN A PROMO:
   GET /promos/{promo_id}/products/

4. CLEAR ALL PRODUCTS FROM A PROMO:
   POST /promos/{promo_id}/clear-products/

5. CREATE A NEW PROMO:
   POST /promos/
   Body: {
     "seller_id": "sid00125",
     "promo_name": "My Promo",
     "promo_description": "Description",
     "discount_amount": 10,
     "is_active": true
   }
    """)

if __name__ == "__main__":
    show_api_usage()
    
    # Uncomment the line below to run the actual tests
    # test_promo_product_management() 
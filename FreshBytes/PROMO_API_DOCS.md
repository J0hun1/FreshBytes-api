# Promo Product Management API Documentation

## Overview
This API allows sellers to manage which products are included in their promos using a many-to-many relationship.

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Create a Promo
**POST** `/promos/`

Create a new promo (initially without products).

**Request Body:**
```json
{
  "seller_id": "sid00125",
  "promo_name": "Summer Sale",
  "promo_description": "20% off on selected items",
  "discount_amount": 20,
  "is_active": true
}
```

**Response:**
```json
{
  "promo_id": "pid00125",
  "seller_id": "sid00125",
  "promo_name": "Summer Sale",
  "promo_description": "20% off on selected items",
  "discount_amount": 20,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### 2. Add Products to a Promo
**POST** `/promos/{promo_id}/add-products/`

Add multiple products to a specific promo.

**Request Body:**
```json
{
  "product_ids": ["prod00125", "prod00225", "prod00325"]
}
```

**Response:**
```json
{
  "message": "Successfully added 3 products to promo pid00125",
  "added_products": ["prod00125", "prod00225", "prod00325"]
}
```

---

### 3. Remove Products from a Promo
**POST** `/promos/{promo_id}/remove-products/`

Remove specific products from a promo.

**Request Body:**
```json
{
  "product_ids": ["prod00125"]
}
```

**Response:**
```json
{
  "message": "Successfully removed 1 products from promo pid00125",
  "removed_products": ["prod00125"]
}
```

---

### 4. Get All Products in a Promo
**GET** `/promos/{promo_id}/products/`

Get all products currently in a specific promo.

**Response:**
```json
{
  "promo_id": "pid00125",
  "products": [
    {
      "product_id": "prod00225",
      "product_name": "Fresh Tomatoes",
      "product_price": "15.99",
      "has_promo": true
    },
    {
      "product_id": "prod00325", 
      "product_name": "Organic Lettuce",
      "product_price": "8.99",
      "has_promo": true
    }
  ],
  "total_products": 2
}
```

---

### 5. Clear All Products from a Promo
**POST** `/promos/{promo_id}/clear-products/`

Remove all products from a promo at once.

**Response:**
```json
{
  "message": "Successfully removed all 2 products from promo pid00125"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "product_ids is required"
}
```

### 404 Not Found
```json
{
  "error": "Promo not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "An error occurred: [error details]"
}
```

---

## Frontend Integration Examples

### JavaScript/React Example
```javascript
// Add products to a promo
const addProductsToPromo = async (promoId, productIds) => {
  try {
    const response = await fetch(`/promos/${promoId}/add-products/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ product_ids: productIds })
    });
    
    const result = await response.json();
    console.log(result.message);
  } catch (error) {
    console.error('Error adding products:', error);
  }
};

// Get products in a promo
const getPromoProducts = async (promoId) => {
  try {
    const response = await fetch(`/promos/${promoId}/products/`);
    const result = await response.json();
    return result.products;
  } catch (error) {
    console.error('Error getting products:', error);
  }
};
```

### Python Example
```python
import requests

# Add products to a promo
def add_products_to_promo(promo_id, product_ids):
    url = f"http://localhost:8000/promos/{promo_id}/add-products/"
    data = {"product_ids": product_ids}
    
    response = requests.post(url, json=data)
    return response.json()

# Usage
result = add_products_to_promo("pid00125", ["prod00125", "prod00225"])
print(result['message'])
```

---

## Automatic Updates

The `has_promo` field on products automatically updates when:
- ✅ Products are added to a promo
- ✅ Products are removed from a promo
- ✅ Promo is activated/deactivated
- ✅ Promo is deleted

This ensures that the product status is always accurate without manual intervention. 
# Promo Product Management - HTTP Methods Summary

## Available Endpoints and HTTP Methods

| Endpoint | HTTP Method | Description | Request Body |
|----------|-------------|-------------|--------------|
| `/promos/` | **POST** | Create a new promo | Promo data |
| `/promos/{promo_id}/add-products/` | **POST** | Add products to a promo | `{"product_ids": ["id1", "id2"]}` |
| `/promos/{promo_id}/remove-products/` | **POST** or **DELETE** | Remove specific products from a promo | `{"product_ids": ["id1", "id2"]}` |
| `/promos/{promo_id}/products/` | **GET** | Get all products in a promo | None |
| `/promos/{promo_id}/clear-products/` | **POST** or **DELETE** | Remove all products from a promo | None |

## RESTful Design

- **POST** - For creating/adding operations
- **GET** - For retrieving data
- **DELETE** - For removing/deleting operations (more RESTful)

## Frontend Usage Examples

### Using POST (Traditional)
```javascript
// Remove products
fetch('/promos/pid00125/remove-products/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({product_ids: ['prod00125']})
});

// Clear all products
fetch('/promos/pid00125/clear-products/', {
  method: 'POST'
});
```

### Using DELETE (More RESTful)
```javascript
// Remove products
fetch('/promos/pid00125/remove-products/', {
  method: 'DELETE',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({product_ids: ['prod00125']})
});

// Clear all products
fetch('/promos/pid00125/clear-products/', {
  method: 'DELETE'
});
```

## Why Both Methods?

- **POST** - More traditional, works with all HTTP clients
- **DELETE** - More RESTful, semantically correct for removal operations
- **Flexibility** - Choose the method that fits your frontend architecture

Both methods work identically - they perform the same operations and return the same responses. 
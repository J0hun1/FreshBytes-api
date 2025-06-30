# FreshBytes API - Visual ERD

## Current Database Schema

```mermaid
erDiagram
    User {
        string user_id PK
        string user_name
        string first_name
        string last_name
        string user_email UK
        string user_password
        string user_phone
        string user_address
        datetime created_at
        datetime updated_at
        boolean is_active
        boolean is_deleted
        boolean is_admin
    }

    Seller {
        string seller_id PK
        string user_id FK
        string business_name
        string business_email
        int business_phone
        string business_address
        decimal total_earnings
        int total_products
        int total_orders
        int total_reviews
        decimal average_rating
        int total_followers
        int total_products_sold
        datetime created_at
        datetime updated_at
        boolean is_active
        boolean is_deleted
    }

    Category {
        int category_id PK
        string category_name UK
        string category_description
        boolean category_isActive
        image category_image
        datetime created_at
        datetime updated_at
    }

    SubCategory {
        string sub_category_id PK
        int category_id FK
        string sub_category_name UK
        string sub_category_description
        image sub_category_image
        datetime created_at
        datetime updated_at
    }

    Product {
        string product_id PK
        string seller_id FK
        string product_name
        decimal product_price
        string product_brief_description
        string product_full_description
        decimal product_discountedPrice
        string product_sku
        string product_status
        string product_location
        int category_id FK
        string sub_category_id FK
        boolean has_promo
        decimal weight
        int quantity
        datetime post_date
        datetime harvest_date
        boolean is_active
        int review_count
        boolean top_rated
        boolean is_srp
        boolean is_discounted
        boolean is_deleted
        int sell_count
        datetime offer_start_date
        datetime offer_end_date
        datetime created_at
        datetime updated_at
    }

    Reviews {
        string review_id PK
        string user_id FK
        string product_id FK
        int review_rating
        string review_comment
        datetime review_date
        datetime created_at
        datetime updated_at
    }

    Promo {
        string promo_id PK
        string seller_id FK
        string promo_name
        string promo_description
        string discount_type
        int discount_amount
        int discount_percentage
        boolean is_active
        datetime promo_start_date
        datetime promo_end_date
        datetime created_at
        datetime updated_at
    }

    Cart {
        string cart_id PK
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    CartItem {
        string cart_item_id PK
        string cart_id FK
        string product_id FK
        int quantity
        decimal total_item_price
        decimal discount_amount
        int discount_percentage
        datetime created_at
        datetime updated_at
    }

    Order {
        string order_id PK
        string user_id FK
        datetime order_date
        decimal order_total
        decimal discount_amount
        int discount_percentage
        string order_status
        datetime created_at
        datetime updated_at
    }

    OrderItem {
        string order_item_id PK
        string order_id FK
        string product_id FK
        int quantity
        decimal total_item_price
        decimal discount_amount
        datetime created_at
        datetime updated_at
    }

    %% Relationships
    User ||--o{ Seller : "has"
    User ||--o{ Reviews : "writes"
    User ||--|| Cart : "has"
    User ||--o{ Order : "places"
    
    Seller ||--o{ Product : "sells"
    Seller ||--o{ Promo : "creates"
    
    Category ||--o{ SubCategory : "contains"
    Category ||--o{ Product : "categorizes"
    SubCategory ||--o{ Product : "subcategorizes"
    
    Product ||--o{ Reviews : "receives"
    Product }o--o{ Promo : "has"
    Product ||--o{ CartItem : "added_to"
    Product ||--o{ OrderItem : "ordered_as"
    
    Cart ||--o{ CartItem : "contains"
    Order ||--o{ OrderItem : "contains"
```

## Key Relationships Summary

| Entity | Relationship | Related Entity | Type |
|--------|-------------|----------------|------|
| User | has | Seller | One-to-Many |
| User | writes | Reviews | One-to-Many |
| User | has | Cart | One-to-One |
| User | places | Order | One-to-Many |
| Seller | sells | Product | One-to-Many |
| Seller | creates | Promo | One-to-Many |
| Category | contains | SubCategory | One-to-Many |
| Category | categorizes | Product | One-to-Many |
| SubCategory | subcategorizes | Product | One-to-Many |
| Product | receives | Reviews | One-to-Many |
| Product | has | Promo | Many-to-Many |
| Product | added_to | CartItem | One-to-Many |
| Product | ordered_as | OrderItem | One-to-Many |
| Cart | contains | CartItem | One-to-Many |
| Order | contains | OrderItem | One-to-Many |

## Data Flow Architecture

```mermaid
graph TD
    A[User Registration] --> B[User Profile]
    B --> C[Seller Registration]
    C --> D[Product Creation]
    D --> E[Product Listing]
    E --> F[User Browsing]
    F --> G[Add to Cart]
    G --> H[Cart Management]
    H --> I[Checkout Process]
    I --> J[Order Creation]
    J --> K[Order Processing]
    K --> L[Order Fulfillment]
    
    M[Reviews] --> E
    N[Promos] --> D
    O[Categories] --> D
    P[SubCategories] --> D
```

## Current System Strengths

✅ **Well-Structured Relationships**
- Clear foreign key relationships
- Proper normalization
- Logical entity separation

✅ **E-commerce Core Features**
- Complete product management
- Shopping cart functionality
- Order processing system
- Review and rating system
- Promotional system

✅ **Data Integrity**
- Custom ID generation
- Timestamp tracking
- Soft delete capabilities
- Status tracking

## Critical Missing Components

❌ **Security & Authentication**
- No user authentication system
- Passwords stored in plain text
- No role-based access control

❌ **Payment Processing**
- No payment model
- No transaction tracking
- No payment status management

❌ **Inventory Management**
- No stock tracking
- No inventory alerts
- No stock reservation system

❌ **Shipping & Delivery**
- No shipping address management
- No delivery tracking
- No shipping cost calculation

❌ **Business Logic**
- No order total calculation
- No inventory validation
- No payment verification
- No order status transitions 
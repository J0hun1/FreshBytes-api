# FreshBytes Entity Relationship Diagram (ERD)

This file contains the Mermaid ERD diagram representing the data model for the FreshBytes API. For more details on the data model and relationships, see the project documentation and `ERD_Analysis.md`.

```mermaid
erDiagram
    USER {
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
    SELLER {
        string seller_id PK
        string user_id FK
        string business_name
        string business_email
        string business_phone
        string business_address
        datetime created_at
        datetime updated_at
        boolean is_active
        boolean is_deleted
    }
    ADDRESS {
        string address_id PK
        string user_id FK
        string type          "billing/shipping"
        string line1
        string line2
        string city
        string region
        string postal_code
        string country
        datetime created_at
        datetime updated_at
    }
    CATEGORY {
        int category_id PK
        string category_name UK
        string category_description
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    SUBCATEGORY {
        string subcategory_id PK
        int category_id FK
        string subcategory_name UK
        string subcategory_description
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    PRODUCT {
        string product_id PK
        string seller_id FK
        int category_id FK
        string subcategory_id FK
        string name
        text brief_description
        text full_description
        decimal price
        string sku
        string status
        string location
        decimal weight
        int quantity
        datetime post_date
        datetime harvest_date
        boolean is_active
        boolean is_deleted
        datetime created_at
        datetime updated_at
    }
    PRODUCTIMAGE {
        string image_id PK
        string product_id FK
        string image_url
        boolean is_primary
    }
    PROMO {
        string promo_id PK
        string seller_id FK
        string name
        string description
        string discount_type    "amount/percentage"
        decimal discount_amount
        int discount_percentage
        datetime start_date
        datetime end_date
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    PROMOPRODUCT {
        string id PK
        string promo_id FK
        string product_id FK
    }
    CART {
        string cart_id PK
        string user_id FK
        datetime created_at
        datetime updated_at
    }
    CARTITEM {
        string cart_item_id PK
        string cart_id FK
        string product_id FK
        int quantity
        decimal unit_price
        decimal discount_amount
        int discount_percentage
        datetime created_at
        datetime updated_at
    }
    "ORDER" {
        string order_id PK
        string user_id FK
        datetime order_date
        decimal total_amount
        decimal discount_amount
        int discount_percentage
        string status
        datetime created_at
        datetime updated_at
    }
    ORDERITEM {
        string order_item_id PK
        string order_id FK
        string product_id FK
        int quantity
        decimal unit_price
        decimal discount_amount
        datetime created_at
        datetime updated_at
    }
    REVIEW {
        string review_id PK
        string user_id FK
        string product_id FK
        int rating
        text comment
        datetime review_date
        datetime created_at
        datetime updated_at
    }
    PAYMENT {
        string payment_id PK
        string order_id FK
        decimal amount
        string method
        string status
        datetime paid_at
    }
    SHIPMENT {
        string shipment_id PK
        string order_id FK
        string carrier
        string tracking_number
        datetime shipped_at
        datetime delivered_at
        string status
    }
    FOLLOWER {
        string follower_id PK
        string seller_id FK
        string user_id FK
        datetime created_at
    }

    USER ||--o{ SELLER         : "has profile"
    USER ||--o{ ADDRESS        : "has"
    USER ||--o{ CART           : "owns"
    USER ||--o{ "ORDER"        : "places"
    USER ||--o{ REVIEW         : "writes"
    USER ||--o{ FOLLOWER       : "follows"

    SELLER ||--o{ PRODUCT       : "sells"
    SELLER ||--o{ PROMO         : "creates"
    SELLER ||--o{ FOLLOWER      : "is followed by"

    CATEGORY ||--o{ SUBCATEGORY : "contains"
    CATEGORY ||--o{ PRODUCT      : "categorizes"

    SUBCATEGORY ||--o{ PRODUCT   : "subcategorizes"

    PRODUCT ||--o{ PRODUCTIMAGE : "has"
    PRODUCT ||--o{ PROMOPRODUCT : "in"
    PRODUCT ||--o{ CARTITEM     : "added to"
    PRODUCT ||--o{ ORDERITEM    : "ordered as"
    PRODUCT ||--o{ REVIEW       : "gets"

    PROMO ||--o{ PROMOPRODUCT   : "applies to"

    PROMOPRODUCT }o--|| PROMO    : "for"
    PROMOPRODUCT }o--|| PRODUCT  : "product"

    CART ||--o{ CARTITEM       : "contains"

    "ORDER" ||--o{ ORDERITEM    : "contains"
    "ORDER" ||--o{ PAYMENT      : "receives"
    "ORDER" ||--o{ SHIPMENT     : "fulfilled by"

    CARTITEM }o--|| CART        : "belongs to"
    CARTITEM }o--|| PRODUCT     : "refers to"

    ORDERITEM }o--|| "ORDER"    : "belongs to"
    ORDERITEM }o--|| PRODUCT     : "refers to"

    REVIEW }o--|| USER          : "by"
    REVIEW }o--|| PRODUCT       : "of"

    PAYMENT }o--|| "ORDER"      : "for"

    SHIPMENT }o--|| "ORDER"     : "for"

    FOLLOWER }o--|| USER        : "by"
    FOLLOWER }o--|| SELLER      : "of"
```

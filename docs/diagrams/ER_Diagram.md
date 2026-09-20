# ER Diagram - Local Farmers Produce Direct-Selling Marketplace

```mermaid
erDiagram

    USERS {
        INTEGER id PK
        TEXT name
        TEXT email
        TEXT password
        TEXT role
    }

    PRODUCTS {
        INTEGER product_id PK
        TEXT product_name
        TEXT category
        REAL price
        INTEGER quantity
        TEXT unit
        INTEGER farmer_id FK
        TEXT image
    }

    ORDERS {
        INTEGER id PK
        INTEGER customer_id FK
        REAL total_amount
        TEXT status
        TIMESTAMP created_at
    }

    ORDER_ITEMS {
        INTEGER id PK
        INTEGER order_id FK
        INTEGER product_id FK
        INTEGER quantity
        REAL price
    }

    CATEGORIES {
        INTEGER id PK
        TEXT name
        TEXT description
    }

    USERS ||--o{ PRODUCTS : adds
    USERS ||--o{ ORDERS : places
    ORDERS ||--o{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : included_in
```
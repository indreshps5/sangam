# Inventory Management Module

## Overview

The Inventory Management module provides comprehensive stock tracking, transaction recording, and alert management for SANGAM logistics operations. It follows SOLID principles with clear separation between routes, services, and repositories.

## Architecture

```
inventory/
├── router.py          # API endpoints (thin controllers)
├── schemas.py         # Pydantic request/response models
├── service.py         # Business logic
├── repository.py      # Data access layer
└── models.py          # SQLAlchemy models (re-exports)
```

### Design Principles

- **Single Responsibility**: Each layer has one job
- **Dependency Inversion**: Service depends on repository interfaces
- **Open/Closed**: Easy to extend without modifying existing code
- **Business Logic**: All rules enforced in service layer, not routes

## API Endpoints

### Inventory Items

#### List Items
```http
GET /api/v1/inventory/items
```

**Query Parameters:**
- `depot_id` (UUID, optional): Filter by depot
- `category` (string, optional): Filter by category
- `search` (string, optional): Search in name, SKU, description
- `low_stock_only` (boolean, optional): Show only low stock items
- `skip` (int, default=0): Pagination offset
- `limit` (int, default=50, max=100): Page size
- `sort_by` (string, default="name"): Sort field
- `sort_order` (string, default="asc"): Sort order (asc/desc)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "depot_id": "uuid",
      "name": "Electronics - Smartphones",
      "sku": "ELEC-SMART-001",
      "category": "Electronics",
      "description": "Latest generation smartphones",
      "unit_of_measure": "units",
      "quantity_on_hand": 1250.0,
      "quantity_reserved": 150.0,
      "quantity_available": 1100.0,
      "min_stock_level": 200.0,
      "max_stock_level": 2000.0,
      "unit_cost": 450.0,
      "currency": "USD",
      "location_code": "A-01-03",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 50
}
```

#### Get Item
```http
GET /api/v1/inventory/items/{item_id}
```

#### Create Item
```http
POST /api/v1/inventory/items
```

**Request Body:**
```json
{
  "depot_id": "uuid",
  "name": "New Product",
  "sku": "PROD-001",
  "category": "Electronics",
  "description": "Product description",
  "unit_of_measure": "units",
  "quantity_on_hand": 100.0,
  "quantity_reserved": 0.0,
  "min_stock_level": 20.0,
  "max_stock_level": 500.0,
  "unit_cost": 50.0,
  "currency": "USD",
  "location_code": "A-01-01"
}
```

**Validation:**
- SKU must be unique within depot
- `quantity_reserved` cannot exceed `quantity_on_hand`
- All quantities must be non-negative

#### Update Item
```http
PUT /api/v1/inventory/items/{item_id}
```

#### Delete Item
```http
DELETE /api/v1/inventory/items/{item_id}
```

### Stock Adjustments

#### Adjust Stock
```http
POST /api/v1/inventory/items/{item_id}/adjust
```

**Request Body:**
```json
{
  "adjustment_type": "receipt|consumption|adjustment",
  "quantity": 50.0,
  "notes": "Stock received from supplier",
  "performed_by": "uuid"
}
```

**Adjustment Types:**
- `receipt`: Add stock (quantity must be positive)
- `consumption`: Remove stock (quantity must be positive, internally negated)
- `adjustment`: Direct adjustment (quantity can be positive or negative)

**Business Rules:**
- Prevents negative stock levels
- Automatically creates transaction records
- Updates `updated_at` timestamp

**Response:**
```json
{
  "id": "uuid",
  "inventory_item_id": "uuid",
  "depot_id": "uuid",
  "transaction_type": "receipt",
  "quantity": 50.0,
  "unit_of_measure": "units",
  "notes": "Stock received from supplier",
  "performed_by": "uuid",
  "performed_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Transfer Stock
```http
POST /api/v1/inventory/items/{item_id}/transfer
```

**Request Body:**
```json
{
  "source_depot_id": "uuid",
  "destination_depot_id": "uuid",
  "quantity": 100.0,
  "notes": "Transfer to Delhi DC",
  "performed_by": "uuid"
}
```

**Business Rules:**
- Creates two transactions (consumption at source, receipt at destination)
- Validates available stock at source
- Requires destination item to exist
- Atomic operation (both succeed or both fail)

**Response:**
```json
{
  "source_transaction": { ... },
  "destination_transaction": { ... }
}
```

### Transactions

#### List Transactions
```http
GET /api/v1/inventory/transactions
```

**Query Parameters:**
- `inventory_item_id` (UUID, optional): Filter by item
- `depot_id` (UUID, optional): Filter by depot
- `transaction_type` (string, optional): Filter by type
- `start_date` (datetime, optional): Start date filter
- `end_date` (datetime, optional): End date filter
- `skip` (int, default=0): Pagination offset
- `limit` (int, default=50, max=100): Page size
- `sort_by` (string, default="performed_at"): Sort field
- `sort_order` (string, default="desc"): Sort order

#### Get Transaction
```http
GET /api/v1/inventory/transactions/{transaction_id}
```

### Alerts

#### Low Stock Alerts
```http
GET /api/v1/inventory/alerts/low-stock
```

**Query Parameters:**
- `depot_id` (UUID, optional): Filter by depot

**Response:**
```json
{
  "alerts": [
    {
      "inventory_item_id": "uuid",
      "item_name": "Perishables - Fresh Produce",
      "sku": "PERISH-PRODUCE-001",
      "depot_id": "uuid",
      "depot_name": "Bangalore Cold Storage",
      "quantity_available": 75.0,
      "min_stock_level": 200.0,
      "shortage": 125.0,
      "unit_of_measure": "kg"
    }
  ],
  "total": 5
}
```

### Statistics

#### Inventory Stats
```http
GET /api/v1/inventory/stats
```

**Query Parameters:**
- `depot_id` (UUID, optional): Filter by depot

**Response:**
```json
{
  "total_items": 150,
  "total_value": 1250000.0,
  "low_stock_count": 12,
  "out_of_stock_count": 3,
  "total_quantity": 45000.0,
  "currency": "USD"
}
```

**Use Case:** Dashboard KPIs consume this endpoint for real-time inventory metrics.

## Database Schema

### Inventory Items Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| depot_id | UUID | FK, NOT NULL, INDEX | Depot where item is stored |
| name | VARCHAR(200) | NOT NULL | Item name |
| sku | VARCHAR(100) | NOT NULL, INDEX | Stock Keeping Unit code |
| category | VARCHAR(100) | INDEX | Product category |
| description | TEXT | | Item description |
| unit_of_measure | VARCHAR(20) | NOT NULL, DEFAULT 'units' | Unit of measurement |
| quantity_on_hand | FLOAT | NOT NULL, DEFAULT 0, CHECK >= 0 | Current stock |
| quantity_reserved | FLOAT | NOT NULL, DEFAULT 0, CHECK >= 0 | Reserved stock |
| min_stock_level | FLOAT | NOT NULL, DEFAULT 0, CHECK >= 0 | Reorder threshold |
| max_stock_level | FLOAT | NOT NULL, DEFAULT 0, CHECK >= 0 | Maximum capacity |
| unit_cost | FLOAT | NOT NULL, DEFAULT 0, CHECK >= 0 | Cost per unit |
| currency | VARCHAR(3) | NOT NULL, DEFAULT 'USD' | ISO 4217 currency |
| location_code | VARCHAR(50) | | Storage location |
| batch_number | VARCHAR(100) | | Batch identifier |
| expiry_date | TIMESTAMPTZ | | Expiration date |
| created_at | TIMESTAMPTZ | NOT NULL, INDEX | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last update timestamp |

**Computed Field:**
- `quantity_available` = `quantity_on_hand` - `quantity_reserved`

### Inventory Transactions Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| inventory_item_id | UUID | FK, NOT NULL, INDEX | Affected item |
| depot_id | UUID | FK, NOT NULL, INDEX | Depot (denormalized) |
| transaction_type | VARCHAR(50) | NOT NULL, INDEX | Type of transaction |
| quantity | FLOAT | NOT NULL, CHECK != 0 | Quantity moved |
| unit_of_measure | VARCHAR(20) | NOT NULL | Unit of measurement |
| reference_id | UUID | INDEX | Related entity ID |
| reference_type | VARCHAR(50) | | Related entity type |
| notes | TEXT | | Transaction notes |
| performed_by | UUID | FK | User who performed |
| performed_at | TIMESTAMPTZ | NOT NULL, INDEX | When performed |
| created_at | TIMESTAMPTZ | NOT NULL, INDEX | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last update timestamp |

**Transaction Types:**
- `receipt`: Stock received
- `shipment`: Stock shipped out
- `transfer`: Stock transferred between depots
- `adjustment`: Manual adjustment
- `consumption`: Stock consumed/used
- `return`: Stock returned

## Business Rules

### Stock Validation

1. **No Negative Stock**: System prevents operations that would result in negative `quantity_on_hand`
2. **Reserved ≤ On Hand**: `quantity_reserved` cannot exceed `quantity_on_hand`
3. **Non-zero Transactions**: All transactions must have non-zero quantity
4. **SKU Uniqueness**: SKU must be unique within a depot

### Concurrency Safety

- Database transactions ensure atomicity
- Check constraints prevent invalid states at database level
- Optimistic locking via `updated_at` timestamp

### Low Stock Alerts

An item is considered "low stock" when:
```
quantity_available < min_stock_level
```

Where:
```
quantity_available = quantity_on_hand - quantity_reserved
```

## Frontend Integration

### React Component

The `InventoryPage` component provides:

- **Stats Cards**: Total items, value, low stock count, out of stock count
- **Low Stock Alerts**: Visual alerts for items below threshold
- **Filters**: Search, depot, category, low stock toggle
- **Sortable Table**: Click column headers to sort
- **Pagination**: Navigate through large datasets
- **Real-time Updates**: Refresh button to reload data

### API Client Usage

```typescript
import { apiClient } from '../lib/api';

// List items with filters
const response = await apiClient.request<{
  items: InventoryItem[];
  total: number;
}>('/inventory/items', {
  params: {
    depot_id: 'uuid',
    category: 'Electronics',
    search: 'smartphone',
    low_stock_only: true,
    skip: 0,
    limit: 50,
    sort_by: 'name',
    sort_order: 'asc',
  },
});

// Adjust stock
await apiClient.request('/inventory/items/{item_id}/adjust', {
  method: 'POST',
  body: JSON.stringify({
    adjustment_type: 'receipt',
    quantity: 100,
    notes: 'Received from supplier',
  }),
});

// Get stats for dashboard
const stats = await apiClient.request<InventoryStats>('/inventory/stats');
```

## Testing

### Unit Tests

```bash
pytest tests/unit/test_inventory_service.py -v
```

**Coverage:**
- Item CRUD operations
- Stock adjustments (receipt, consumption, adjustment)
- Validation rules (negative stock, duplicate SKU, etc.)
- Low stock alerts
- Statistics calculations

### Integration Tests

```bash
pytest tests/integration/test_inventory_api.py -v
```

**Coverage:**
- All API endpoints
- Authentication and authorization
- Query parameters and filters
- Error handling
- Response formats

## Seed Data

The seed script creates sample inventory data:

```bash
cd apps/api
python -m sangam_api.scripts.seed
```

**Created Data:**
- 9 inventory items across 3 depots
- 4 sample transactions
- 1 low stock item (for testing alerts)

**Sample Items:**
- Mumbai: Electronics (smartphones, laptops), Packaging materials
- Delhi: Consumer goods (beverages, snacks), Office supplies
- Bangalore: Perishables (dairy, frozen, produce) - includes low stock example

## Dashboard Integration

The inventory stats endpoint (`/api/v1/inventory/stats`) provides KPIs for the dashboard:

```typescript
// Dashboard KPIs
const stats = await apiClient.request<InventoryStats>('/inventory/stats');

// Display in dashboard
<div>Total Items: {stats.total_items}</div>
<div>Total Value: {stats.currency} {stats.total_value.toLocaleString()}</div>
<div>Low Stock: {stats.low_stock_count}</div>
<div>Out of Stock: {stats.out_of_stock_count}</div>
```

## Security

- All endpoints require authentication
- Permission checks: `inventory:read`, `inventory:write`
- Audit logging for all stock adjustments
- No sensitive data in responses

## Performance

- Indexed columns for fast queries
- Pagination to limit result sets
- Efficient filtering at database level
- Computed fields calculated in application layer

## Future Enhancements

- [ ] Bulk import/export (CSV, Excel)
- [ ] Barcode/QR code scanning
- [ ] Automated reorder suggestions
- [ ] Integration with procurement module
- [ ] Historical trend analysis
- [ ] Warehouse capacity optimization
- [ ] Multi-unit conversions
- [ ] Batch/lot tracking
- [ ] Expiry date alerts

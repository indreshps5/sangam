# Inventory Management - Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Backend and frontend running

## 1. Seed the Database

```bash
cd apps/api
python -m sangam_api.scripts.seed
```

This creates:
- 3 depots (Mumbai, Delhi, Bangalore)
- 9 inventory items
- 4 sample transactions
- 1 low stock item (for testing alerts)

## 2. Start the Backend

```bash
cd apps/api
uvicorn sangam_api.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

## 3. Start the Frontend

```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## 4. Login

Open http://localhost:3000 in your browser.

**Demo Credentials:**

| Role | Email | Password |
|------|-------|----------|
| Inventory Manager | inventory@sangam.dev | inventory123! |
| Admin | admin@sangam.dev | admin123! |

## 5. Navigate to Inventory

After login, navigate to: http://localhost:3000/inventory

Or click "Inventory" in the navigation menu.

## 6. Explore Features

### View Inventory
- See all inventory items in a sortable table
- View stock levels, locations, and categories
- Check last updated timestamps

### Filter & Search
- **Search**: Type in the search box to filter by name, SKU, or description
- **Depot Filter**: Select a specific depot from the dropdown
- **Category Filter**: Select a category (Electronics, Consumer Goods, etc.)
- **Low Stock Toggle**: Check "Low Stock Only" to see items below threshold

### Sort Data
Click column headers to sort:
- Item name
- SKU
- Available stock
- Min stock level
- Last updated

### View Alerts
- **Stats Cards**: See total items, value, low stock count, out of stock count
- **Low Stock Panel**: Items below minimum stock level with shortage amounts

### Pagination
- Navigate through pages using Previous/Next buttons
- See current page and total items

## 7. Test API Endpoints

### List Items
```bash
curl http://localhost:8000/api/v1/inventory/items \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Stats
```bash
curl http://localhost:8000/api/v1/inventory/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Low Stock Alerts
```bash
curl http://localhost:8000/api/v1/inventory/alerts/low-stock \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Adjust Stock
```bash
curl -X POST http://localhost:8000/api/v1/inventory/items/ITEM_ID/adjust \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "adjustment_type": "receipt",
    "quantity": 50.0,
    "notes": "Test receipt"
  }'
```

## 8. Run Tests

### Unit Tests
```bash
cd apps/api
pytest tests/unit/test_inventory_service.py -v
```

### Integration Tests
```bash
cd apps/api
pytest tests/integration/test_inventory_api.py -v
```

## 9. Sample Data

### Depots
1. **Mumbai Central Warehouse** (WH-MUM-001)
   - Electronics (smartphones, laptops)
   - Packaging materials

2. **Delhi Distribution Center** (DC-DEL-001)
   - Consumer goods (beverages, snacks)
   - Office supplies

3. **Bangalore Cold Storage** (CS-BLR-001)
   - Perishables (dairy, frozen, produce)
   - Includes low stock example

### Low Stock Example
- **Item**: Perishables - Fresh Produce
- **Depot**: Bangalore Cold Storage
- **Available**: 75 kg
- **Min Stock**: 200 kg
- **Shortage**: 125 kg

This item will appear in the low stock alerts panel.

## 10. Common Operations

### Search for an Item
1. Type "smartphone" in the search box
2. Results filter automatically
3. Clear search to see all items

### Filter by Depot
1. Select "Mumbai Central Warehouse" from depot dropdown
2. Table shows only Mumbai items
3. Select "All Depots" to reset

### View Low Stock Items
1. Check "Low Stock Only" toggle
2. Table shows only items below minimum stock
3. Orange warning icon indicates low stock

### Sort by Stock Level
1. Click "Available Stock" column header
2. Click again to toggle asc/desc
3. See items sorted by stock level

### Navigate Pages
1. If more than 20 items, pagination appears
2. Click "Next" to see next page
3. Click "Previous" to go back

## 11. Dashboard Integration

The inventory stats endpoint provides KPIs for the dashboard:

```typescript
// Fetch stats
const stats = await apiClient.request('/inventory/stats');

// Display in dashboard
<div>Total Items: {stats.total_items}</div>
<div>Total Value: ${stats.total_value.toLocaleString()}</div>
<div>Low Stock: {stats.low_stock_count}</div>
<div>Out of Stock: {stats.out_of_stock_count}</div>
```

## 12. Troubleshooting

### "No inventory items found"
- Run seed script: `python -m sangam_api.scripts.seed`
- Check backend is running on port 8000
- Verify authentication token is valid

### "Failed to fetch inventory data"
- Check backend is running
- Verify API URL in `.env` file
- Check browser console for errors

### Low stock alerts not showing
- Check if any items are below minimum stock level
- Verify `min_stock_level` is set for items
- Refresh the page

### Cannot adjust stock
- Verify you have `inventory:write` permission
- Check item exists and is not deleted
- Ensure quantity is valid (positive for receipt, not exceeding stock for consumption)

## 13. API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Markdown**: docs/INVENTORY.md

## 14. Next Steps

1. ✅ Explore the inventory page
2. ✅ Test filtering and search
3. ✅ Try stock adjustments via API
4. ✅ Run the test suite
5. ✅ Review the documentation
6. ✅ Integrate with dashboard
7. ✅ Add more inventory items
8. ✅ Customize categories and units

## 15. Support

- **Documentation**: docs/INVENTORY.md
- **API Reference**: http://localhost:8000/docs
- **Tests**: tests/unit/test_inventory_service.py
- **Implementation**: INVENTORY_IMPLEMENTATION.md

---

**You're all set!** 🎉

The inventory management system is ready to use with sample data and comprehensive features.

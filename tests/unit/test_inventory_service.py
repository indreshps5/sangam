"""
Unit tests for inventory service.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from sangam_api.inventory.service import InventoryService
from sangam_api.inventory.models import InventoryItem, InventoryTransaction
from sangam_api.inventory.schemas import (
    InventoryItemCreate,
    InventoryItemUpdate,
    StockAdjustmentRequest,
    StockTransferRequest,
)
from sangam_api.core.exceptions import (
    NotFoundException,
    ValidationException,
    ConflictException,
)


class MockItemRepository:
    """Mock repository for inventory items."""
    
    def __init__(self):
        self.items = {}
    
    async def get_by_id(self, item_id):
        return self.items.get(item_id)
    
    async def get_by_sku(self, depot_id, sku):
        for item in self.items.values():
            if item.depot_id == depot_id and item.sku == sku:
                return item
        return None
    
    async def list_items(self, **kwargs):
        return list(self.items.values())
    
    async def count_items(self, **kwargs):
        return len(self.items)
    
    async def create(self, item):
        self.items[item.id] = item
        return item
    
    async def update(self, item):
        self.items[item.id] = item
        return item
    
    async def delete(self, item_id):
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False
    
    async def get_low_stock_items(self, depot_id=None):
        low_stock = []
        for item in self.items.values():
            available = item.quantity_on_hand - item.quantity_reserved
            if available < item.min_stock_level:
                low_stock.append(item)
        return low_stock


class MockTransactionRepository:
    """Mock repository for inventory transactions."""
    
    def __init__(self):
        self.transactions = {}
    
    async def get_by_id(self, transaction_id):
        return self.transactions.get(transaction_id)
    
    async def list_transactions(self, **kwargs):
        return list(self.transactions.values())
    
    async def count_transactions(self, **kwargs):
        return len(self.transactions)
    
    async def create(self, transaction):
        self.transactions[transaction.id] = transaction
        return transaction


@pytest.fixture
def item_repo():
    return MockItemRepository()


@pytest.fixture
def transaction_repo():
    return MockTransactionRepository()


@pytest.fixture
def service(item_repo, transaction_repo):
    return InventoryService(item_repo, transaction_repo)


@pytest.fixture
def sample_item():
    depot_id = uuid4()
    return InventoryItem(
        id=uuid4(),
        depot_id=depot_id,
        name="Test Item",
        sku="TEST-001",
        category="Test",
        unit_of_measure="units",
        quantity_on_hand=100.0,
        quantity_reserved=10.0,
        min_stock_level=20.0,
        max_stock_level=200.0,
        unit_cost=10.0,
        currency="USD",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_item(service, item_repo):
    """Test creating a new inventory item."""
    depot_id = uuid4()
    item_data = InventoryItemCreate(
        depot_id=depot_id,
        name="New Item",
        sku="NEW-001",
        category="Test",
        unit_of_measure="units",
        quantity_on_hand=50.0,
        quantity_reserved=5.0,
        min_stock_level=10.0,
        max_stock_level=100.0,
        unit_cost=15.0,
        currency="USD",
    )
    
    result = await service.create_item(item_data)
    
    assert result.name == "New Item"
    assert result.sku == "NEW-001"
    assert result.quantity_on_hand == 50.0
    assert result.quantity_available == 45.0


@pytest.mark.asyncio
async def test_create_item_duplicate_sku(service, item_repo, sample_item):
    """Test creating an item with duplicate SKU raises error."""
    item_repo.items[sample_item.id] = sample_item
    
    item_data = InventoryItemCreate(
        depot_id=sample_item.depot_id,
        name="Another Item",
        sku=sample_item.sku,  # Same SKU
        category="Test",
        unit_of_measure="units",
        quantity_on_hand=50.0,
        quantity_reserved=0.0,
        min_stock_level=10.0,
        max_stock_level=100.0,
        unit_cost=15.0,
        currency="USD",
    )
    
    with pytest.raises(ConflictException):
        await service.create_item(item_data)


@pytest.mark.asyncio
async def test_create_item_reserved_exceeds_on_hand(service):
    """Test creating an item with reserved > on_hand raises error."""
    item_data = InventoryItemCreate(
        depot_id=uuid4(),
        name="Invalid Item",
        sku="INV-001",
        category="Test",
        unit_of_measure="units",
        quantity_on_hand=50.0,
        quantity_reserved=60.0,  # More than on_hand
        min_stock_level=10.0,
        max_stock_level=100.0,
        unit_cost=15.0,
        currency="USD",
    )
    
    with pytest.raises(ValidationException):
        await service.create_item(item_data)


@pytest.mark.asyncio
async def test_get_item(service, item_repo, sample_item):
    """Test getting an inventory item by ID."""
    item_repo.items[sample_item.id] = sample_item
    
    result = await service.get_item(sample_item.id)
    
    assert result.id == sample_item.id
    assert result.name == sample_item.name
    assert result.quantity_available == 90.0


@pytest.mark.asyncio
async def test_get_item_not_found(service):
    """Test getting a non-existent item raises error."""
    with pytest.raises(NotFoundException):
        await service.get_item(uuid4())


@pytest.mark.asyncio
async def test_adjust_stock_receipt(service, item_repo, transaction_repo, sample_item):
    """Test receiving stock."""
    item_repo.items[sample_item.id] = sample_item
    
    adjustment = StockAdjustmentRequest(
        adjustment_type="receipt",
        quantity=50.0,
        notes="Test receipt",
    )
    
    result = await service.adjust_stock(sample_item.id, adjustment)
    
    assert result.transaction_type == "receipt"
    assert result.quantity == 50.0
    
    # Check item was updated
    updated_item = item_repo.items[sample_item.id]
    assert updated_item.quantity_on_hand == 150.0


@pytest.mark.asyncio
async def test_adjust_stock_consumption(service, item_repo, transaction_repo, sample_item):
    """Test consuming stock."""
    item_repo.items[sample_item.id] = sample_item
    
    adjustment = StockAdjustmentRequest(
        adjustment_type="consumption",
        quantity=30.0,
        notes="Test consumption",
    )
    
    result = await service.adjust_stock(sample_item.id, adjustment)
    
    assert result.transaction_type == "consumption"
    assert result.quantity == -30.0
    
    # Check item was updated
    updated_item = item_repo.items[sample_item.id]
    assert updated_item.quantity_on_hand == 70.0


@pytest.mark.asyncio
async def test_adjust_stock_insufficient_quantity(service, item_repo, sample_item):
    """Test consuming more than available raises error."""
    item_repo.items[sample_item.id] = sample_item
    
    adjustment = StockAdjustmentRequest(
        adjustment_type="consumption",
        quantity=200.0,  # More than on_hand
        notes="Invalid consumption",
    )
    
    with pytest.raises(ValidationException, match="Insufficient stock"):
        await service.adjust_stock(sample_item.id, adjustment)


@pytest.mark.asyncio
async def test_adjust_stock_invalid_type(service, item_repo, sample_item):
    """Test invalid adjustment type raises error."""
    item_repo.items[sample_item.id] = sample_item
    
    adjustment = StockAdjustmentRequest(
        adjustment_type="invalid_type",
        quantity=50.0,
        notes="Invalid type",
    )
    
    with pytest.raises(ValidationException, match="Invalid adjustment type"):
        await service.adjust_stock(sample_item.id, adjustment)


@pytest.mark.asyncio
async def test_get_low_stock_alerts(service, item_repo):
    """Test getting low stock alerts."""
    # Create items with different stock levels
    depot_id = uuid4()
    
    low_stock_item = InventoryItem(
        id=uuid4(),
        depot_id=depot_id,
        name="Low Stock Item",
        sku="LOW-001",
        unit_of_measure="units",
        quantity_on_hand=15.0,
        quantity_reserved=5.0,
        min_stock_level=20.0,  # Available (10) < min (20)
        max_stock_level=100.0,
        unit_cost=10.0,
        currency="USD",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    normal_item = InventoryItem(
        id=uuid4(),
        depot_id=depot_id,
        name="Normal Item",
        sku="NORM-001",
        unit_of_measure="units",
        quantity_on_hand=50.0,
        quantity_reserved=5.0,
        min_stock_level=20.0,  # Available (45) > min (20)
        max_stock_level=100.0,
        unit_cost=10.0,
        currency="USD",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    item_repo.items[low_stock_item.id] = low_stock_item
    item_repo.items[normal_item.id] = normal_item
    
    alerts, total = await service.get_low_stock_alerts()
    
    assert total == 1
    assert alerts[0].inventory_item_id == low_stock_item.id
    assert alerts[0].shortage == 10.0  # min (20) - available (10)


@pytest.mark.asyncio
async def test_get_inventory_stats(service, item_repo):
    """Test getting inventory statistics."""
    depot_id = uuid4()
    
    # Create multiple items
    for i in range(3):
        item = InventoryItem(
            id=uuid4(),
            depot_id=depot_id,
            name=f"Item {i}",
            sku=f"ITEM-{i:03d}",
            unit_of_measure="units",
            quantity_on_hand=100.0 * (i + 1),
            quantity_reserved=10.0,
            min_stock_level=20.0,
            max_stock_level=500.0,
            unit_cost=10.0,
            currency="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        item_repo.items[item.id] = item
    
    stats = await service.get_inventory_stats()
    
    assert stats.total_items == 3
    assert stats.total_quantity == 600.0  # 100 + 200 + 300
    assert stats.total_value == 6000.0  # 600 * 10
    assert stats.currency == "USD"

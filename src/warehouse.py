"""
Warehouse Model

Each Warehouse object represents a physical warehouse node in the supply chain.
Internally uses a HashMap for O(1) product lookups by SKU.
"""

from src.hash_map import HashMap


class Warehouse:
    """
    A single warehouse in the global supply chain network.

    Attributes:
        warehouse_id : Unique identifier (e.g. "WH_DELHI", "WH_MUMBAI")
        location     : City / region name
        inventory    : HashMap { sku → { "name", "price", "stock", "category" } }
    """

    def __init__(self, warehouse_id: str, location: str):
        self.warehouse_id = warehouse_id
        self.location = location
        self.inventory: HashMap = HashMap()   # SKU → product dict

    # ------------------------------------------------------------------
    # Inventory CRUD
    # ------------------------------------------------------------------
    def add_product(self, sku: str, name: str, price: float, stock: int, category: str = "General"):
        """Add a new product or overwrite if SKU already exists."""
        self.inventory.put(sku, {
            "sku": sku,
            "name": name,
            "price": price,
            "stock": stock,
            "category": category,
            "warehouse_id": self.warehouse_id
        })

    def get_product(self, sku: str) -> dict:
        """Retrieve product details. O(1)."""
        return self.inventory.get(sku)

    def update_stock(self, sku: str, delta: int) -> bool:
        """
        Adjust stock by delta (+ve = restock, -ve = sale/shipment).
        Returns False if product not found or stock would go negative.
        """
        product = self.inventory.get(sku)
        if product is None:
            return False
        new_stock = product["stock"] + delta
        if new_stock < 0:
            return False
        product["stock"] = new_stock
        self.inventory.put(sku, product)
        return True

    def update_price(self, sku: str, new_price: float) -> bool:
        product = self.inventory.get(sku)
        if product is None:
            return False
        product["price"] = new_price
        self.inventory.put(sku, product)
        return True

    def remove_product(self, sku: str) -> bool:
        return self.inventory.delete(sku)

    def get_stock(self, sku: str) -> int:
        """Quick stock-level check for Dijkstra nearest-warehouse logic."""
        product = self.inventory.get(sku)
        return product["stock"] if product else 0

    def all_products(self) -> list:
        return self.inventory.values()

    def product_count(self) -> int:
        return self.inventory.size()

    def __repr__(self):
        return f"Warehouse({self.warehouse_id} @ {self.location}, {self.product_count()} SKUs)"

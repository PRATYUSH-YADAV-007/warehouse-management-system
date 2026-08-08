"""
Inventory Manager — Central Coordinator

Ties all four data structures together:
  ┌─────────────────────────────────────────────────────────┐
  │  HashMap       → O(1) product/order lookup by ID/SKU   │
  │  Trie          → O(m) prefix product search             │
  │  Red-Black Tree→ O(log n) sorted order management       │
  │  Dijkstra      → O((V+E)logV) nearest-warehouse routing │
  └─────────────────────────────────────────────────────────┘
"""

import uuid
from datetime import datetime

from src.hash_map import HashMap
from src.trie import Trie
from src.red_black_tree import RedBlackTree
from src.dijkstra import Dijkstra, Graph
from src.warehouse import Warehouse


ORDER_STATUSES = ["PENDING", "CONFIRMED", "DISPATCHED", "IN_TRANSIT", "DELIVERED", "CANCELLED"]


class InventoryManager:

    def __init__(self):
        # ── Warehouses ─────────────────────────────────────────────────────────
        self.warehouses: HashMap = HashMap()          # wh_id → Warehouse object

        # ── Global product index (SKU → warehouse_id list) ────────────────────
        self.product_index: HashMap = HashMap()       # sku → [wh_id, ...]

        # ── Trie for fast product name prefix search ───────────────────────────
        self.product_trie: Trie = Trie()

        # ── Red-Black Tree for order management (key=order_id int, val=order dict)
        self.order_tree: RedBlackTree = RedBlackTree()
        self._order_counter: int = 1000             # auto-increment numeric key

        # ── HashMap for O(1) order status lookups ─────────────────────────────
        self.order_map: HashMap = HashMap()          # order_id_str → order dict

        # ── Delivery network (graph for Dijkstra) ─────────────────────────────
        self.delivery_graph: Graph = Graph()
        self.dijkstra: Dijkstra = Dijkstra(self.delivery_graph)

    # ==========================================================================
    # WAREHOUSE MANAGEMENT
    # ==========================================================================
    def add_warehouse(self, warehouse_id: str, location: str) -> Warehouse:
        wh = Warehouse(warehouse_id, location)
        self.warehouses.put(warehouse_id, wh)
        self.delivery_graph.add_node(warehouse_id)
        return wh

    def get_warehouse(self, warehouse_id: str):
        return self.warehouses.get(warehouse_id)

    def list_warehouses(self) -> list:
        return self.warehouses.values()

    def add_route(self, wh1: str, wh2: str, distance_km: float):
        """Add a delivery route between two warehouse nodes."""
        self.delivery_graph.add_edge(wh1, wh2, distance_km)

    # ==========================================================================
    # PRODUCT MANAGEMENT
    # ==========================================================================
    def add_product(self, warehouse_id: str, sku: str, name: str,
                    price: float, stock: int, category: str = "General") -> bool:
        wh: Warehouse = self.warehouses.get(warehouse_id)
        if wh is None:
            return False

        # Add to warehouse's internal HashMap
        wh.add_product(sku, name, price, stock, category)

        # Update global product index
        existing = self.product_index.get(sku) or []
        if warehouse_id not in existing:
            existing.append(warehouse_id)
        self.product_index.put(sku, existing)

        # Insert into Trie for prefix search
        self.product_trie.insert(name, sku)

        return True

    def get_product(self, sku: str, warehouse_id: str = None) -> dict:
        """
        O(1) lookup via HashMap.
        If warehouse_id given → query that warehouse only.
        Else → find first warehouse that has this SKU.
        """
        if warehouse_id:
            wh = self.warehouses.get(warehouse_id)
            return wh.get_product(sku) if wh else None

        wh_ids = self.product_index.get(sku) or []
        for wid in wh_ids:
            wh = self.warehouses.get(wid)
            if wh:
                p = wh.get_product(sku)
                if p:
                    return p
        return None

    def search_products_by_prefix(self, prefix: str) -> list:
        """
        Trie prefix search: O(m) — find all product names starting with prefix.
        Returns list of (name, [skus]) tuples.
        """
        return self.product_trie.starts_with(prefix)

    def update_stock(self, warehouse_id: str, sku: str, delta: int) -> bool:
        wh = self.warehouses.get(warehouse_id)
        if wh is None:
            return False
        return wh.update_stock(sku, delta)

    def update_price(self, warehouse_id: str, sku: str, new_price: float) -> bool:
        wh = self.warehouses.get(warehouse_id)
        if wh is None:
            return False
        return wh.update_price(sku, new_price)

    def total_stock_across_warehouses(self, sku: str) -> dict:
        """Return { warehouse_id: stock_count } for this SKU across all warehouses."""
        wh_ids = self.product_index.get(sku) or []
        result = {}
        for wid in wh_ids:
            wh = self.warehouses.get(wid)
            if wh:
                stock = wh.get_stock(sku)
                result[wid] = stock
        return result

    # ==========================================================================
    # ORDER MANAGEMENT  (Red-Black Tree + HashMap)
    # ==========================================================================
    def place_order(self, customer_name: str, sku: str, quantity: int,
                    customer_location: str) -> dict:
        """
        Place a new order:
          1. Find nearest warehouse with stock (Dijkstra)
          2. Deduct stock
          3. Record order in RBT (sorted by order_id) and HashMap (O(1) lookup)
        """
        # ── Find nearest warehouse using Dijkstra ──────────────────────────────
        wh_ids = self.product_index.get(sku) or []
        warehouses_stock = {}
        for wid in wh_ids:
            wh = self.warehouses.get(wid)
            if wh:
                warehouses_stock[wid] = wh.get_stock(sku)

        if not warehouses_stock:
            return {"error": f"Product SKU '{sku}' not found in any warehouse."}

        # Add customer location node temporarily if not in graph
        if customer_location not in self.delivery_graph.adj:
            self.delivery_graph.add_node(customer_location)

        best_wh, distance, path = self.dijkstra.nearest_warehouse_with_stock(
            customer_location, warehouses_stock, quantity
        )

        # Fallback: if customer_location has no routes, pick warehouse with highest stock
        if best_wh is None:
            best_wh = max(warehouses_stock, key=warehouses_stock.get)
            stock = warehouses_stock[best_wh]
            if stock < quantity:
                return {"error": f"Insufficient stock. Max available: {stock} units."}
            distance = 0
            path = [best_wh]

        if best_wh is None:
            return {"error": "No warehouse has sufficient stock for this order."}

        # ── Deduct stock ───────────────────────────────────────────────────────
        success = self.update_stock(best_wh, sku, -quantity)
        if not success:
            return {"error": "Stock deduction failed unexpectedly."}

        # ── Get product details ────────────────────────────────────────────────
        wh_obj = self.warehouses.get(best_wh)
        product = wh_obj.get_product(sku)

        # ── Build order record ─────────────────────────────────────────────────
        order_id_int = self._order_counter
        self._order_counter += 1
        order_id_str = f"ORD{order_id_int}"

        order = {
            "order_id": order_id_str,
            "customer_name": customer_name,
            "customer_location": customer_location,
            "sku": sku,
            "product_name": product["name"] if product else sku,
            "quantity": quantity,
            "unit_price": product["price"] if product else 0,
            "total_price": round((product["price"] if product else 0) * quantity, 2),
            "warehouse_id": best_wh,
            "warehouse_location": wh_obj.location,
            "delivery_distance_km": round(distance, 2),
            "delivery_path": path,
            "status": "CONFIRMED",
            "placed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Insert into RBT (key=int for sorted traversal) and HashMap (O(1) access)
        self.order_tree.insert(order_id_int, order)
        self.order_map.put(order_id_str, order)

        return order

    def get_order(self, order_id_str: str) -> dict:
        """O(1) order lookup via HashMap."""
        return self.order_map.get(order_id_str)

    def update_order_status(self, order_id_str: str, new_status: str) -> bool:
        """Update status in both HashMap and RBT. O(1) + O(log n)."""
        if new_status.upper() not in ORDER_STATUSES:
            return False

        order = self.order_map.get(order_id_str)
        if order is None:
            return False

        order["status"] = new_status.upper()
        order["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update HashMap
        self.order_map.put(order_id_str, order)

        # Update RBT node value
        order_id_int = int(order_id_str.replace("ORD", ""))
        self.order_tree.update(order_id_int, order)

        return True

    def cancel_order(self, order_id_str: str) -> bool:
        """Cancel order and restock inventory."""
        order = self.order_map.get(order_id_str)
        if order is None:
            return False
        if order["status"] in ("DELIVERED", "CANCELLED"):
            return False

        # Restock
        self.update_stock(order["warehouse_id"], order["sku"], order["quantity"])
        return self.update_order_status(order_id_str, "CANCELLED")

    def all_orders_sorted(self) -> list:
        """Return all orders sorted by order_id (RBT inorder traversal). O(n)."""
        return [val for _, val in self.order_tree.inorder()]

    def orders_by_status(self, status: str) -> list:
        """Filter orders by status."""
        return [o for o in self.all_orders_sorted()
                if o["status"] == status.upper()]

    # ==========================================================================
    # ROUTING
    # ==========================================================================
    def find_best_route(self, from_node: str, to_node: str):
        """Return (distance, path) between two nodes in the delivery network."""
        return self.dijkstra.shortest_path_to(from_node, to_node)

    def nearest_warehouse_for_sku(self, sku: str, customer_location: str, qty: int = 1):
        """Public helper wrapping Dijkstra nearest-warehouse search."""
        wh_ids = self.product_index.get(sku) or []
        warehouses_stock = {}
        for wid in wh_ids:
            wh = self.warehouses.get(wid)
            if wh:
                warehouses_stock[wid] = wh.get_stock(sku)

        if customer_location not in self.delivery_graph.adj:
            self.delivery_graph.add_node(customer_location)

        return self.dijkstra.nearest_warehouse_with_stock(
            customer_location, warehouses_stock, qty
        )

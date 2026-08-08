"""
╔══════════════════════════════════════════════════════════════╗
║        GLOBAL E-COMMERCE SUPPLY CHAIN & INVENTORY MANAGER    ║
║              DSA Project — G-11, 3rd Semester                ║
╠══════════════════════════════════════════════════════════════╣
║  Data Structures Used:                                        ║
║   • Red-Black Tree  → Order management  (O log n)            ║
║   • Trie            → Product prefix search  (O m)           ║
║   • HashMap         → Product/Order lookup  (O 1)            ║
║   • Dijkstra's Algo → Nearest warehouse routing              ║
╚══════════════════════════════════════════════════════════════╝

Run:  python main.py
"""

import sys
import os

# Make sure src/ is importable regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.inventory_manager import InventoryManager, ORDER_STATUSES
from data.seed_data import seed


# ─── Pretty printers ──────────────────────────────────────────────────────────

def divider(char="─", width=60):
    print(char * width)

def header(text):
    print()
    divider("═")
    print(f"  {text}")
    divider("═")

def subheader(text):
    print(f"\n  ── {text} ──")

def success(msg):   print(f"\n  ✔  {msg}")
def error(msg):     print(f"\n  ✘  {msg}")
def info(msg):      print(f"     {msg}")

def print_product(p: dict):
    if not p:
        return
    print(f"     SKU      : {p.get('sku','')}")
    print(f"     Name     : {p.get('name','')}")
    print(f"     Category : {p.get('category','')}")
    print(f"     Price    : ₹{p.get('price', 0):,.2f}")
    print(f"     Stock    : {p.get('stock', 0)} units")
    print(f"     Warehouse: {p.get('warehouse_id','')} ({p.get('warehouse_location','') or ''})")

def print_order(o: dict):
    if not o:
        return
    print(f"     Order ID  : {o.get('order_id','')}")
    print(f"     Customer  : {o.get('customer_name','')}  ({o.get('customer_location','')})")
    print(f"     Product   : {o.get('product_name','')}  [SKU: {o.get('sku','')}]")
    print(f"     Quantity  : {o.get('quantity','')}")
    print(f"     Unit Price: ₹{o.get('unit_price', 0):,.2f}")
    print(f"     Total     : ₹{o.get('total_price', 0):,.2f}")
    print(f"     Status    : {o.get('status','')}")
    print(f"     Warehouse : {o.get('warehouse_id','')} ({o.get('warehouse_location','')})")
    dist = o.get('delivery_distance_km', 0)
    path = o.get('delivery_path', [])
    if dist:
        print(f"     Distance  : {dist} km")
    if path:
        print(f"     Route     : {' → '.join(path)}")
    print(f"     Placed At : {o.get('placed_at','')}")
    print(f"     Updated At: {o.get('updated_at','')}")

def prompt(msg: str, default: str = "") -> str:
    val = input(f"  > {msg}: ").strip()
    return val if val else default

def prompt_int(msg: str, default: int = 0) -> int:
    try:
        return int(prompt(msg, str(default)))
    except ValueError:
        return default

def prompt_float(msg: str, default: float = 0.0) -> float:
    try:
        return float(prompt(msg, str(default)))
    except ValueError:
        return default


# ─── Menu Handlers ────────────────────────────────────────────────────────────

def menu_warehouses(manager: InventoryManager):
    while True:
        header("WAREHOUSE MANAGEMENT")
        print("  1. List all warehouses")
        print("  2. Add new warehouse")
        print("  3. Add delivery route between warehouses")
        print("  4. Find shortest route between two nodes")
        print("  0. Back")
        choice = prompt("Choice")

        if choice == "1":
            subheader("All Warehouses")
            whs = manager.list_warehouses()
            if not whs:
                info("No warehouses found.")
            for wh in whs:
                info(f"[{wh.warehouse_id}]  {wh.location}  —  {wh.product_count()} SKUs")

        elif choice == "2":
            wid  = prompt("Warehouse ID (e.g. WH_KOCHI)").upper()
            loc  = prompt("Location / City name")
            if wid and loc:
                manager.add_warehouse(wid, loc)
                success(f"Warehouse '{wid}' added at {loc}.")
            else:
                error("ID and location are required.")

        elif choice == "3":
            wh1  = prompt("From Warehouse ID").upper()
            wh2  = prompt("To Warehouse ID").upper()
            dist = prompt_float("Distance (km)")
            manager.add_route(wh1, wh2, dist)
            success(f"Route {wh1} ↔ {wh2} ({dist} km) added.")

        elif choice == "4":
            subheader("Shortest Delivery Route  [Dijkstra's Algorithm]")
            src = prompt("From node (warehouse ID or city)").upper()
            dst = prompt("To node").upper()
            distance, path = manager.find_best_route(src, dst)
            if not path:
                error("No route found.")
            else:
                info(f"Distance : {distance:.1f} km")
                info(f"Path     : {' → '.join(path)}")

        elif choice == "0":
            break


def menu_products(manager: InventoryManager):
    while True:
        header("PRODUCT & INVENTORY MANAGEMENT")
        print("  1. Search products by name/prefix  [Trie]")
        print("  2. Lookup product by SKU  [HashMap O(1)]")
        print("  3. View stock across all warehouses")
        print("  4. Add new product to a warehouse")
        print("  5. Update stock (restock / adjustment)")
        print("  6. Update price")
        print("  7. List all products in a warehouse")
        print("  0. Back")
        choice = prompt("Choice")

        if choice == "1":
            subheader("Prefix Product Search  [Trie]")
            prefix = prompt("Enter product name or prefix")
            results = manager.search_products_by_prefix(prefix)
            if not results:
                info("No products found matching that prefix.")
            else:
                info(f"Found {len(results)} match(es):")
                for name, skus in results:
                    info(f"  '{name}'  →  SKUs: {', '.join(skus)}")

        elif choice == "2":
            subheader("Product Lookup by SKU  [HashMap]")
            sku = prompt("SKU").upper()
            wid = prompt("Warehouse ID (leave blank for any)")
            p = manager.get_product(sku, wid.upper() if wid else None)
            if p:
                print_product(p)
            else:
                error("Product not found.")

        elif choice == "3":
            subheader("Stock Across Warehouses")
            sku = prompt("SKU").upper()
            stock_map = manager.total_stock_across_warehouses(sku)
            if not stock_map:
                error("Product not found in any warehouse.")
            else:
                total = sum(stock_map.values())
                for wid, qty in stock_map.items():
                    wh = manager.get_warehouse(wid)
                    info(f"  {wid} ({wh.location if wh else ''}) : {qty} units")
                info(f"  {'─'*35}")
                info(f"  Total stock : {total} units")

        elif choice == "4":
            subheader("Add Product")
            wid      = prompt("Warehouse ID").upper()
            sku      = prompt("SKU").upper()
            name     = prompt("Product Name")
            price    = prompt_float("Price (₹)")
            stock    = prompt_int("Initial Stock")
            category = prompt("Category (default: General)", "General")
            ok = manager.add_product(wid, sku, name, price, stock, category)
            if ok:
                success(f"Product '{name}' (SKU: {sku}) added to {wid}.")
            else:
                error(f"Warehouse '{wid}' not found.")

        elif choice == "5":
            subheader("Update Stock")
            wid   = prompt("Warehouse ID").upper()
            sku   = prompt("SKU").upper()
            delta = prompt_int("Change in stock (+ restock / - sale). e.g. 50 or -10")
            ok    = manager.update_stock(wid, sku, delta)
            if ok:
                new_stock = manager.get_product(sku, wid)
                success(f"Stock updated. New stock: {new_stock['stock'] if new_stock else 'N/A'}")
            else:
                error("Update failed. Check warehouse ID, SKU, and ensure stock won't go negative.")

        elif choice == "6":
            subheader("Update Price")
            wid   = prompt("Warehouse ID").upper()
            sku   = prompt("SKU").upper()
            price = prompt_float("New Price (₹)")
            ok    = manager.update_price(wid, sku, price)
            success("Price updated.") if ok else error("Update failed.")

        elif choice == "7":
            subheader("All Products in Warehouse")
            wid = prompt("Warehouse ID").upper()
            wh  = manager.get_warehouse(wid)
            if not wh:
                error("Warehouse not found.")
            else:
                products = wh.all_products()
                if not products:
                    info("No products in this warehouse.")
                else:
                    info(f"{len(products)} product(s) in {wid} ({wh.location}):\n")
                    for p in products:
                        info(f"  [{p['sku']}]  {p['name']}  —  ₹{p['price']:,.0f}  —  {p['stock']} units  —  {p['category']}")

        elif choice == "0":
            break


def menu_orders(manager: InventoryManager):
    while True:
        header("ORDER MANAGEMENT")
        print("  1. Place new order  [Dijkstra nearest warehouse]")
        print("  2. Track order by ID  [HashMap O(1)]")
        print("  3. Update order status")
        print("  4. Cancel order")
        print("  5. View all orders  [Red-Black Tree inorder]")
        print("  6. Filter orders by status")
        print("  7. Find nearest warehouse for a product  [Dijkstra]")
        print("  0. Back")
        choice = prompt("Choice")

        if choice == "1":
            subheader("Place New Order  [Dijkstra's Algorithm for warehouse selection]")
            customer = prompt("Customer Name")
            location = prompt("Customer Location / City (e.g. CUSTOMER_NOIDA, WH_DELHI)").upper()
            sku      = prompt("Product SKU").upper()
            qty      = prompt_int("Quantity")
            if not all([customer, location, sku, qty]):
                error("All fields are required.")
                continue
            order = manager.place_order(customer, sku, qty, location)
            if "error" in order:
                error(order["error"])
            else:
                success("Order placed successfully!")
                print()
                print_order(order)

        elif choice == "2":
            subheader("Track Order  [HashMap O(1)]")
            oid = prompt("Order ID (e.g. ORD1000)").upper()
            o   = manager.get_order(oid)
            if o:
                print_order(o)
            else:
                error("Order not found.")

        elif choice == "3":
            subheader("Update Order Status")
            oid    = prompt("Order ID").upper()
            print(f"  Statuses: {', '.join(ORDER_STATUSES)}")
            status = prompt("New Status").upper()
            ok = manager.update_order_status(oid, status)
            success(f"Status updated to {status}.") if ok else error("Update failed. Check order ID and status.")

        elif choice == "4":
            subheader("Cancel Order")
            oid = prompt("Order ID").upper()
            ok  = manager.cancel_order(oid)
            if ok:
                success("Order cancelled. Stock has been restocked.")
            else:
                error("Cancellation failed. Order may not exist or is already delivered/cancelled.")

        elif choice == "5":
            subheader("All Orders  [Red-Black Tree Inorder Traversal — Sorted by Order ID]")
            orders = manager.all_orders_sorted()
            if not orders:
                info("No orders yet.")
            else:
                info(f"Total orders: {len(orders)}\n")
                for o in orders:
                    divider("-", 50)
                    print_order(o)

        elif choice == "6":
            subheader("Filter Orders by Status")
            print(f"  Statuses: {', '.join(ORDER_STATUSES)}")
            status = prompt("Status").upper()
            orders = manager.orders_by_status(status)
            if not orders:
                info(f"No orders with status '{status}'.")
            else:
                info(f"{len(orders)} order(s) with status '{status}':\n")
                for o in orders:
                    divider("-", 50)
                    print_order(o)

        elif choice == "7":
            subheader("Nearest Warehouse for Product  [Dijkstra's Algorithm]")
            sku      = prompt("Product SKU").upper()
            location = prompt("Your Location / City").upper()
            qty      = prompt_int("Quantity needed", 1)
            best_wh, dist, path = manager.nearest_warehouse_for_sku(sku, location, qty)
            if best_wh is None:
                error("No warehouse found with sufficient stock or no route available.")
            else:
                success(f"Nearest warehouse: {best_wh}")
                info(f"Distance : {dist:.1f} km")
                info(f"Route    : {' → '.join(path)}")

        elif choice == "0":
            break


def demo_mode(manager: InventoryManager):
    """Run a quick automated demo showing all DSA features."""
    header("DEMO MODE  —  All DSA Features")

    print("\n  [1/4] TRIE — Prefix Product Search")
    divider()
    results = manager.search_products_by_prefix("sam")
    info("Searching for products starting with 'sam':")
    for name, skus in results:
        info(f"  '{name}'  →  {', '.join(skus)}")

    print("\n  [2/4] HASHMAP — O(1) Product Lookup")
    divider()
    p = manager.get_product("ELEC001")
    info("Fetching ELEC001 (Samsung Galaxy S24):")
    if p:
        info(f"  Name: {p['name']}  |  Price: ₹{p['price']:,}  |  Stock: {p['stock']}")

    print("\n  [3/4] DIJKSTRA — Nearest Warehouse Routing")
    divider()
    best, dist, path = manager.nearest_warehouse_for_sku("ELEC001", "CUSTOMER_NOIDA", 5)
    info("Finding nearest warehouse for 5× ELEC001 from CUSTOMER_NOIDA:")
    info(f"  Best warehouse : {best}")
    info(f"  Distance       : {dist:.1f} km")
    info(f"  Route          : {' → '.join(path)}")

    print("\n  [4/4] RED-BLACK TREE — Order Tracking")
    divider()
    info("Placing 3 orders and listing them via RBT inorder traversal:")
    for cust, sku, qty, loc in [
        ("Rahul Sharma",  "ELEC001",  2, "CUSTOMER_NOIDA"),
        ("Priya Mehta",   "HOME001",  1, "CUSTOMER_THANE"),
        ("Arjun Nair",    "BOOK001",  3, "CUSTOMER_COCHIN"),
    ]:
        o = manager.place_order(cust, sku, qty, loc)
        if "error" not in o:
            info(f"  {o['order_id']}  {o['customer_name']}  {o['product_name']}  ×{o['quantity']}  ₹{o['total_price']:,}")

    info("\n  All orders sorted by Order ID (RBT inorder):")
    for o in manager.all_orders_sorted():
        info(f"   {o['order_id']}  |  {o['customer_name']}  |  {o['status']}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 62)
    print("  GLOBAL E-COMMERCE SUPPLY CHAIN & INVENTORY MANAGEMENT")
    print("  DSA Project — G-11  |  3rd Semester")
    print("═" * 62)
    print("\n  Initializing system and loading seed data...")

    manager = InventoryManager()
    seed(manager)

    print(f"  ✔  {len(manager.list_warehouses())} warehouses loaded")
    print(f"  ✔  Delivery network built")
    print(f"  ✔  Products indexed in Trie + HashMap")
    print("\n  System ready.\n")

    while True:
        header("MAIN MENU")
        print("  1. Warehouse Management")
        print("  2. Product & Inventory Management")
        print("  3. Order Management")
        print("  4. Run Demo  (shows all 4 DSA features)")
        print("  0. Exit")
        divider()
        choice = prompt("Choice")

        if choice == "1":
            menu_warehouses(manager)
        elif choice == "2":
            menu_products(manager)
        elif choice == "3":
            menu_orders(manager)
        elif choice == "4":
            demo_mode(manager)
        elif choice == "0":
            print("\n  Goodbye!\n")
            sys.exit(0)
        else:
            error("Invalid choice. Please enter 0–4.")


if __name__ == "__main__":
    main()

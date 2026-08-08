"""
Seed Data — Pre-populates the system with realistic warehouses,
products, and delivery network routes for demo/testing.
"""

from src.inventory_manager import InventoryManager


def seed(manager: InventoryManager):
    """Populate manager with sample warehouses, products, and delivery routes."""

    # ── Warehouses ─────────────────────────────────────────────────────────────
    warehouses = [
        ("WH_DELHI",   "Delhi"),
        ("WH_MUMBAI",  "Mumbai"),
        ("WH_CHENNAI", "Chennai"),
        ("WH_KOLKATA", "Kolkata"),
        ("WH_PUNE",    "Pune"),
        ("WH_HYDERABAD","Hyderabad"),
    ]
    for wid, loc in warehouses:
        manager.add_warehouse(wid, loc)

    # ── Delivery Network (distances in km) ─────────────────────────────────────
    # Approximate inter-city distances
    routes = [
        ("WH_DELHI",    "WH_MUMBAI",    1415),
        ("WH_DELHI",    "WH_KOLKATA",    1305),
        ("WH_DELHI",    "WH_HYDERABAD",  1575),
        ("WH_MUMBAI",   "WH_PUNE",        150),
        ("WH_MUMBAI",   "WH_HYDERABAD",   711),
        ("WH_MUMBAI",   "WH_CHENNAI",    1338),
        ("WH_PUNE",     "WH_HYDERABAD",   561),
        ("WH_HYDERABAD","WH_CHENNAI",     629),
        ("WH_HYDERABAD","WH_KOLKATA",    1492),
        ("WH_CHENNAI",  "WH_KOLKATA",    1659),
        # Customer city connections
        ("WH_DELHI",    "CUSTOMER_NOIDA",   20),
        ("WH_MUMBAI",   "CUSTOMER_THANE",   30),
        ("WH_PUNE",     "CUSTOMER_NASHIK",  210),
        ("WH_DELHI",    "CUSTOMER_AGRA",    200),
        ("WH_CHENNAI",  "CUSTOMER_COCHIN",  650),
    ]
    for r in routes:
        manager.add_route(*r)

    # ── Products ───────────────────────────────────────────────────────────────
    # (warehouse_id, sku, name, price, stock, category)
    products = [
        # Electronics
        ("WH_DELHI",     "ELEC001", "Samsung Galaxy S24",      79999, 120, "Electronics"),
        ("WH_MUMBAI",    "ELEC001", "Samsung Galaxy S24",      79999,  85, "Electronics"),
        ("WH_HYDERABAD", "ELEC001", "Samsung Galaxy S24",      79999,  40, "Electronics"),

        ("WH_DELHI",     "ELEC002", "Sony WH-1000XM5 Headphones", 29999, 200, "Electronics"),
        ("WH_CHENNAI",   "ELEC002", "Sony WH-1000XM5 Headphones", 29999,  60, "Electronics"),

        ("WH_MUMBAI",    "ELEC003", "Apple MacBook Air M3",   114999,  30, "Electronics"),
        ("WH_DELHI",     "ELEC003", "Apple MacBook Air M3",   114999,  20, "Electronics"),

        ("WH_KOLKATA",   "ELEC004", "Samsung 65-inch QLED TV",  89999,  15, "Electronics"),
        ("WH_PUNE",      "ELEC004", "Samsung 65-inch QLED TV",  89999,  10, "Electronics"),

        # Home & Kitchen
        ("WH_MUMBAI",    "HOME001", "Philips Air Fryer",       5999, 300, "Home & Kitchen"),
        ("WH_PUNE",      "HOME001", "Philips Air Fryer",       5999, 150, "Home & Kitchen"),
        ("WH_DELHI",     "HOME001", "Philips Air Fryer",       5999, 250, "Home & Kitchen"),

        ("WH_HYDERABAD", "HOME002", "Prestige Pressure Cooker", 1799, 500, "Home & Kitchen"),
        ("WH_CHENNAI",   "HOME002", "Prestige Pressure Cooker", 1799, 400, "Home & Kitchen"),

        # Sports
        ("WH_DELHI",     "SPRT001", "Nivia Football",          799,  600, "Sports"),
        ("WH_KOLKATA",   "SPRT001", "Nivia Football",          799,  800, "Sports"),

        ("WH_MUMBAI",    "SPRT002", "Yonex Badminton Racket",  2499, 350, "Sports"),
        ("WH_HYDERABAD", "SPRT002", "Yonex Badminton Racket",  2499, 200, "Sports"),

        # Books
        ("WH_DELHI",     "BOOK001", "Data Structures and Algorithms in Python", 499, 1000, "Books"),
        ("WH_MUMBAI",    "BOOK001", "Data Structures and Algorithms in Python", 499,  800, "Books"),

        ("WH_CHENNAI",   "BOOK002", "Introduction to Algorithms (CLRS)",       999,  500, "Books"),
        ("WH_KOLKATA",   "BOOK002", "Introduction to Algorithms (CLRS)",       999,  300, "Books"),

        # Clothing
        ("WH_MUMBAI",    "CLTH001", "Levi's 511 Slim Jeans",  2499, 400, "Clothing"),
        ("WH_PUNE",      "CLTH001", "Levi's 511 Slim Jeans",  2499, 250, "Clothing"),

        ("WH_HYDERABAD", "CLTH002", "Nike Dri-FIT T-Shirt",   1299, 700, "Clothing"),
        ("WH_DELHI",     "CLTH002", "Nike Dri-FIT T-Shirt",   1299, 500, "Clothing"),
    ]

    for args in products:
        manager.add_product(*args)

    return manager

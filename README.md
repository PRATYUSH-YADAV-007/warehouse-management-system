# Global E-Commerce Supply Chain & Inventory Management
### DSA Project — G-11, 3rd Semester

> **Leveraging Advanced Data Structures for Optimized Supply Chain Efficiency**

---

## Project Overview

A terminal-based Warehouse Management System that applies four core Data Structures and Algorithms taught in the course to solve real-world e-commerce supply chain problems.

---

## Data Structures & Algorithms Used

| DSA | Where Applied | Time Complexity |
|-----|--------------|----------------|
| **Red-Black Tree** | Customer order management & status tracking (sorted by order ID) | O(log n) insert / search / delete |
| **Trie (Prefix Tree)** | Fast product name search and autocomplete | O(m) — m = query length |
| **HashMap** | O(1) product SKU lookup, order ID → status mapping | O(1) average |
| **Dijkstra's Algorithm** | Nearest warehouse selection, shortest delivery route | O((V+E) log V) |

---

## Project Structure

```
warehouse_management_system/
│
├── main.py                    # Entry point — terminal menu system
│
├── src/
│   ├── red_black_tree.py      # Full RBT with insert / delete / search / fixup
│   ├── trie.py                # Prefix tree with insert / search / starts_with / delete
│   ├── hash_map.py            # Custom HashMap with chaining & rehashing
│   ├── dijkstra.py            # Dijkstra's with min-heap; nearest-warehouse finder
│   ├── warehouse.py           # Warehouse model (uses HashMap internally)
│   └── inventory_manager.py   # Central coordinator — ties all DSA together
│
└── data/
    └── seed_data.py           # Pre-loaded 6 warehouses, 26 products, delivery network
```

---

## How to Run

```bash
# No external dependencies — pure Python 3
python main.py
```

### Menu Options

```
MAIN MENU
  1. Warehouse Management       → Add warehouses, routes, find shortest paths
  2. Product & Inventory        → Add products, search by prefix (Trie), update stock/price
  3. Order Management           → Place orders (auto-routes via Dijkstra), track, cancel
  4. Run Demo                   → Automated showcase of all 4 DSA features
  0. Exit
```

---

## Key Features

### 1. Red-Black Tree — Order Management
- All orders stored in a self-balancing BST, keyed by order ID
- Guarantees O(log n) insert/search/delete regardless of insertion order
- Inorder traversal returns all orders sorted by ID

### 2. Trie — Product Search
- Product names indexed character-by-character
- `search_products_by_prefix("sam")` returns all products starting with "sam" in O(m)
- Outperforms HashMap for prefix/autocomplete operations
- Supports hierarchical category representation

### 3. HashMap — Product & Order Lookup
- Custom implementation with polynomial rolling hash + separate chaining
- Auto-rehashes when load factor exceeds 0.75 (doubles capacity)
- O(1) SKU → product details, O(1) order ID → order status
- Prevents duplication; always reflects latest stock/price

### 4. Dijkstra's Algorithm — Warehouse Routing
- Delivery network modeled as a weighted undirected graph
- On every order, finds the **nearest warehouse with sufficient stock**
- Supports rerouting around delays (remove edge, re-run algorithm)
- Pre-computed delivery route shown on every order

---

## Sample Data

**Warehouses:** Delhi, Mumbai, Chennai, Kolkata, Pune, Hyderabad

**Products:** Samsung Galaxy S24, MacBook Air M3, Sony WH-1000XM5, Philips Air Fryer, Nivia Football, Yonex Badminton Racket, Levi's Jeans, Nike T-Shirt, CLRS Book, and more.

**Delivery Network:** Real approximate inter-city distances (km) between all warehouse cities.

---

## Why These Data Structures?

| Problem | Naive Approach | Our Approach |
|---------|---------------|--------------|
| Find product by SKU | Linear scan O(n) | HashMap O(1) |
| Search by product name prefix | String compare O(n·m) | Trie O(m) |
| Maintain sorted order log | Sort every time O(n log n) | RBT O(log n) per op |
| Find nearest warehouse | Check all warehouses O(V²) | Dijkstra O((V+E)log V) |

---

## Team
- Aditya Suresh — CB.SC.U4CSE23602
- Kaushal Loya — CB.SC.U4CSE23627
- Paarthu Reddy — CB.SC.U4CSE23639
- Pratyush Yadav — CB.SC.U4CSE23641
- Priyansh Narang — CB.SC.U4CSE23642

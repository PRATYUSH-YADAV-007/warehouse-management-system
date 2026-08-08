import heapq
import time 
def loading():
    print("\nLoading, please wait", end="", flush=True)
    for _ in range(4):
        time.sleep(0.5)      # Total delay = 2 seconds
        print(".", end="", flush=True)
    print("\n")

# Red-Black Tree for Inventory Management
class Node:
    def __init__(self, key, color, product_name=None, stock_per_warehouse=None, price=0, left=None, right=None):
        self.key = key  # SKU
        self.color = color  # Red or Black
        self.product_name = product_name
        self.stock_per_warehouse = stock_per_warehouse or {}  # Stock in each warehouse
        self.price = price  # Product price
        self.left = left
        self.right = right
        self.parent = None


class RedBlackTree:
    def __init__(self):
        self.TNULL = Node(0, "black")  # Sentinel node
        self.root = self.TNULL

    def insert(self, key, product_name, stock_per_warehouse, price):
        new_node = Node(key, "red", product_name, stock_per_warehouse, price)
        new_node.left = self.TNULL
        new_node.right = self.TNULL
        new_node.parent = None

        parent_node = None
        current_node = self.root

        while current_node != self.TNULL:
            parent_node = current_node
            if new_node.key < current_node.key:
                current_node = current_node.left
            else:
                current_node = current_node.right

        new_node.parent = parent_node

        if parent_node is None:
            self.root = new_node
        elif new_node.key < parent_node.key:
            parent_node.left = new_node
        else:
            parent_node.right = new_node

    def search(self, node, key):
        if node == self.TNULL or key == node.key:
            return node
        if key < node.key:
            return self.search(node.left, key)
        return self.search(node.right, key)

    def update_stock(self, sku, warehouse, quantity):
        node = self.search(self.root, sku)
        if node != self.TNULL and warehouse in node.stock_per_warehouse:
            if node.stock_per_warehouse[warehouse] >= quantity:
                node.stock_per_warehouse[warehouse] -= quantity
                return True
            return False
        return False

    def revert_stock(self, sku, warehouse, quantity):
        node = self.search(self.root, sku)
        if node != self.TNULL and warehouse in node.stock_per_warehouse:
            node.stock_per_warehouse[warehouse] += quantity
            return True
        return False


#--------------------------------------------------------------------------------------------------------------------------------------------

# Trie + Hash Map for Product Search and Retrieval
class TrieNode:
    def __init__(self):
        self.children = {}
        self.isEndOfWord = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.isEndOfWord = True

    def autocomplete(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._find_words(node, prefix)

    def _find_words(self, node, prefix):
        words = []
        if node.isEndOfWord:
            words.append(prefix)
        for char, child_node in node.children.items():
            words += self._find_words(child_node, prefix + char)
        return words

#---------------------------------------------------------------------------------------------------------------------------------------------

class ProductDatabase:
    def __init__(self, rbt_inventory):
        self.rbt_inventory = rbt_inventory
        self.trie = Trie()

    def add_product(self, sku, name, details):
        self.rbt_inventory.insert(sku, name, details["stock_per_warehouse"], details["price"])
        self.trie.insert(name)

    def find_product(self, name_prefix):
        matching_products = self.trie.autocomplete(name_prefix)
        if matching_products:
            print(f"Products found for '{name_prefix}':")
            for product in matching_products:
                node = self.rbt_inventory.search(self.rbt_inventory.root, self.get_sku_by_name(product))
                if node != self.rbt_inventory.TNULL:
                    print(f"{product} - Price: Rs {node.price}, Total Stock: {sum(node.stock_per_warehouse.values())}")
        else:
            print("No matching products found.")

    def get_sku_by_name(self, product_name):
        name_to_sku = {
            "Smartphone": 101,
            "Toothpaste": 102,
            "Calculator": 103,
            "Refrigerator": 104,
            "Chair": 105,          # New product SKU
            "ToothBrush": 106,     # New product SKU
        }
        return name_to_sku.get(product_name, None)

#-----------------------------------------------------------------------------------------------------------------------------------------------

# Hash Map for Order Status Tracking
class OrderTracker:
    def __init__(self):
        self.orders = {}  # Order ID -> Status
        self.next_order_id = 1001  # To generate unique order IDs

    def add_order(self, status):
        order_id = self.next_order_id
        self.orders[order_id] = status
        self.next_order_id += 1
        return order_id  # Return the generated order ID

    def get_order_status(self, order_id):
        return self.orders.get(order_id, "Order not found")

    def remove_order(self, order_id):
        if order_id in self.orders:
            del self.orders[order_id]
            return True
        return False

    def view_orders(self):
        return self.orders

#---------------------------------------------------------------------------------------------------------------------------------------

# Dijkstra's Algorithm for Delivery Route Optimization
def dijkstra(graph, start):
    queue = [(0, start)]
    distances = {node: float("infinity") for node in graph}
    distances[start] = 0

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))

    return distances

#---------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------

def menu():
    # Initialize the graph (warehouses and distances between cities and warehouses)
    graph = {
        "Coimbatore": [("Ettimadai", 10), ("Chennai", 100), ("Hyderabad", 600), ("Mumbai", 800), ("Delhi", 1800), ("Jaipur", 2000)],
        "Ettimadai": [("Coimbatore", 10), ("Chennai", 100)],
        "Chennai": [("Coimbatore", 100), ("Ettimadai", 100), ("Hyderabad", 500), ("Mumbai", 1000), ("Delhi", 1500), ("Jaipur", 1700)],
        "Delhi": [("Mumbai", 1400), ("Chennai", 1500), ("Hyderabad", 1200), ("Jaipur", 250)],
        "Hyderabad": [("Chennai", 500), ("Delhi", 1200), ("Mumbai", 700), ("Jaipur", 1300)],
        "Mumbai": [("Hyderabad", 700), ("Jaipur", 1100), ("Delhi", 1400)],
        "Jaipur": [("Delhi", 250), ("Mumbai", 1100), ("Hyderabad", 1300)],
    }


    # Initialize Red-Black Tree for inventory management
    rbt_inventory = RedBlackTree()

    # Initialize Product Database using RBT
    product_db = ProductDatabase(rbt_inventory)

    # Adding products with individual stock inputs
    products = [
        {"sku": 101, "name": "SmartPhone", "price": 200},
        {"sku": 102, "name": "Toothpaste", "price": 50},
        {"sku": 103, "name": "Calculator", "price": 10},
        {"sku": 104, "name": "Headphones", "price": 200},
        {"sku": 105, "name": "ToothBrush", "price": 15},
    ]

    for product in products:
        stock_per_warehouse = {}
        for warehouse in ["Coimbatore", "Ettimadai", "Chennai", "Delhi"]:
            stock = int(input(f"Enter total stock for {product['name']} in {warehouse}: "))
            stock_per_warehouse[warehouse] = stock
        
        product_db.add_product(product["sku"], product["name"], {
            "stock_per_warehouse": stock_per_warehouse,
            "price": product["price"]
        })
        
    # Prompt user for delivery location
    print("----------------------------------------------------------------------------------------------------------------------------")
    print("----------------------------------------------------------------------------------------------------------------------------")
    print(" ")
    print("Welcome!")
    print(" ")
    delivery_location = input(
        "Enter your delivery location (Hyderabad, Mumbai, Delhi, Chennai, Jaipur): "
    )

    tracker = OrderTracker()
    
    while True:
        print("\n==== MENU ====")
        print("1. View available items")
        print("2. Search for items")
        print("3. Add a new order")
        print("4. Track an order")
        print("5. View all orders")
        print("6. Remove an order")
        print("7. Warehouse Distribution")
        print("8. Exit")


        choice = input("Enter your choice: ")
        loading()
        if choice == "1":
            print(" ")
            print("Inventory of available items:")
            print("  Product      Price     Stock")
            def display_simple_inventory(node):
                if node != rbt_inventory.TNULL:
                    display_simple_inventory(node.left)
                    total_stock = sum(node.stock_per_warehouse.values())
                    if total_stock>0:
                        print(f"{node.product_name}     Rs.{node.price}      {total_stock}")
                    else:
                        print(f"{node.product_name}     Rs.{node.price}      OUT OF STOCK ")
                    display_simple_inventory(node.right)

            display_simple_inventory(rbt_inventory.root)
            
        elif choice == "2":
            loading()
            search_query = input("Enter product name to search: ")
            print(" ")
            product_db.find_product(search_query)

        elif choice == "3":
            loading()
            product_name = input("Enter the product name to place an order: ")
            quantity = int(input(f"Enter the quantity required for {product_name}: "))
            sku = product_db.get_sku_by_name(product_name)

            if sku:
                node = product_db.rbt_inventory.search(product_db.rbt_inventory.root, sku)
                if node != product_db.rbt_inventory.TNULL:
                    total_stock = sum(node.stock_per_warehouse.values())
                    if total_stock > 0:
                        # Calculate distances to all warehouses from the delivery location
                        distances_from_delivery = dijkstra(graph, delivery_location)
                        # Sort warehouses by proximity to the delivery location
                        sorted_warehouses = sorted(node.stock_per_warehouse.keys(), key=lambda w: distances_from_delivery[w])

                        remaining_quantity = quantity  # Track remaining quantity to fulfill
                        used_warehouses = []  # Track warehouses used to fulfill order
                        for warehouse in sorted_warehouses:
                            if remaining_quantity <= 0:
                                break  # Break if order is fulfilled
                            available_stock = node.stock_per_warehouse[warehouse]
                            if available_stock > 0:
                                used_warehouses.append(warehouse)
                                if available_stock >= remaining_quantity:
                                    node.stock_per_warehouse[warehouse] -= remaining_quantity
                                    remaining_quantity = 0  # Order fulfilled
                                else:
                                    remaining_quantity -= available_stock
                                    node.stock_per_warehouse[warehouse] = 0  # Deplete this warehouse's stock

                        # Determine order status based on the number of warehouses involved
                        if len(used_warehouses) == 1:
                            if used_warehouses[0] == delivery_location:
                                order_status = "Out for Delivery"
                            else:
                                order_status = "Dispatched"
                        elif len(used_warehouses) == 2:
                            order_status = "Shipped"
                        else:
                            order_status = "Order Placed"

                        # Track the order with the appropriate status
                        tracker.add_order(f"{product_name} Qty: {quantity} - {order_status}")
                        print(f"Order placed successfully!")
                        
                        if remaining_quantity > 0:
                            print(f"Only {quantity - remaining_quantity} of {product_name} could be fulfilled. Out of stock for the remaining {remaining_quantity}.")
                    else:
                        print("Insufficient stock in inventory.")
                else:
                    print("Product not found.")
            else:
                print("Product not found.")

        elif choice == "4":
            loading()
            order_id = int(input("Enter your order ID: "))
            status = tracker.get_order_status(order_id)
            print(f"Order ID {order_id}: {status}")

        elif choice == "5":
            loading()
            orders = tracker.view_orders()
            if orders:
                print("Current orders:")
                i=1
                for order_id, status in orders.items():
                    print(f"{i}. Order ID: {order_id} - Status: {status}")
                    i=i+1
            else:
                print("No orders found.")

        elif choice == "6":
            loading()
            if not tracker.orders:
                print("No orders to be removed.")
            else:
                order_id = int(input("Enter your order ID to remove: "))
                if tracker.remove_order(order_id):
                    print("Order removed successfully.")
                else:
                    print("No order found.")

        elif choice == "7":
            loading()
            print("Detailed Inventory:")
            def display_detailed_inventory(node):
                if node != rbt_inventory.TNULL:
                    display_detailed_inventory(node.left)
                    total_stock = sum(node.stock_per_warehouse.values())
                    distribution = ", ".join(
                        [f"{warehouse}: {qty}" for warehouse, qty in node.stock_per_warehouse.items()]
                    )
                    print(
                        f"SKU ID: {node.key}   Product: {node.product_name}   Price: Rs {node.price}   "
                        f"Distribution: ({distribution})   Stock: {total_stock}"
                    )
                    display_detailed_inventory(node.right)

            display_detailed_inventory(rbt_inventory.root)
        elif choice == "8":
            break

        else:
            print("Invalid choice. Please try again.")
            
if __name__ == "__main__":
    menu()
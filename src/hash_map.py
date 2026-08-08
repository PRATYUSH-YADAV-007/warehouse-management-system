"""
HashMap - Used for:
  - O(1) average-case lookup of product details by SKU/product_id
  - Order-ID → order-status mapping (dispatched, in-transit, delivered)
  - Prevents data duplication; always provides up-to-date info
  - Stores: stock levels, location, pricing, descriptions, categories

Implements separate chaining for collision resolution.
Load factor threshold = 0.75 → triggers rehashing.
"""


class _HashNode:
    """Single entry in a chain."""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None  # linked list for chaining


class HashMap:
    """
    Custom HashMap with separate chaining and dynamic resizing.
    Guarantees O(1) amortized for insert, lookup, delete.
    """

    DEFAULT_CAPACITY = 16
    LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self._capacity = capacity
        self._size = 0
        self._buckets = [None] * self._capacity

    # -------------------------------------------------------------------------
    # Hash Function
    # -------------------------------------------------------------------------
    def _hash(self, key) -> int:
        """Polynomial rolling hash for string keys; fallback to built-in hash."""
        if isinstance(key, str):
            h = 0
            prime = 31
            for ch in key:
                h = (h * prime + ord(ch)) % self._capacity
            return h
        return hash(key) % self._capacity

    # -------------------------------------------------------------------------
    # Core operations
    # -------------------------------------------------------------------------
    def put(self, key, value):
        """Insert or update key-value pair. O(1) average."""
        if self._size / self._capacity >= self.LOAD_FACTOR_THRESHOLD:
            self._rehash()

        idx = self._hash(key)
        node = self._buckets[idx]

        # Walk chain looking for existing key
        while node:
            if node.key == key:
                node.value = value  # update
                return
            node = node.next

        # Prepend new node (O(1))
        new_node = _HashNode(key, value)
        new_node.next = self._buckets[idx]
        self._buckets[idx] = new_node
        self._size += 1

    def get(self, key):
        """Return value for key, or None if missing. O(1) average."""
        idx = self._hash(key)
        node = self._buckets[idx]
        while node:
            if node.key == key:
                return node.value
            node = node.next
        return None

    def delete(self, key) -> bool:
        """Remove key from map. Returns True if found. O(1) average."""
        idx = self._hash(key)
        node = self._buckets[idx]
        prev = None
        while node:
            if node.key == key:
                if prev:
                    prev.next = node.next
                else:
                    self._buckets[idx] = node.next
                self._size -= 1
                return True
            prev = node
            node = node.next
        return False

    def contains(self, key) -> bool:
        return self.get(key) is not None

    def keys(self) -> list:
        """Return all keys in the map."""
        result = []
        for bucket in self._buckets:
            node = bucket
            while node:
                result.append(node.key)
                node = node.next
        return result

    def values(self) -> list:
        result = []
        for bucket in self._buckets:
            node = bucket
            while node:
                result.append(node.value)
                node = node.next
        return result

    def items(self) -> list:
        result = []
        for bucket in self._buckets:
            node = bucket
            while node:
                result.append((node.key, node.value))
                node = node.next
        return result

    def size(self) -> int:
        return self._size

    # -------------------------------------------------------------------------
    # Rehashing
    # -------------------------------------------------------------------------
    def _rehash(self):
        """Double capacity and re-insert all entries. Amortized O(1) per op."""
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [None] * self._capacity
        self._size = 0

        for bucket in old_buckets:
            node = bucket
            while node:
                self.put(node.key, node.value)
                node = node.next

    def __repr__(self):
        return f"HashMap(size={self._size}, capacity={self._capacity})"

    def update(self, key, field: str, new_val):
        """
        Convenience: update a single field inside a dict value.
        e.g. update("SKU001", "stock", 50)
        """
        data = self.get(key)
        if data and isinstance(data, dict):
            data[field] = new_val
            self.put(key, data)
            return True
        return False

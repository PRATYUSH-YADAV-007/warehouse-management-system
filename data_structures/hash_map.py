"""
HashMap (Hash Table) Implementation — separate chaining
Used for: O(1) average lookup for:
          - Product details by SKU / product_id
          - Order status by order_id
          - Warehouse stock levels
          - Preventing data duplication
"""


class HashNode:
    """Single entry in a chain."""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashMap:
    """
    Custom hash map with separate chaining for collision resolution.
    Average O(1) for insert, search, delete.
    Automatically resizes when load factor exceeds 0.75.
    """

    DEFAULT_CAPACITY = 64
    LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.capacity = capacity
        self.size = 0
        self.buckets = [None] * self.capacity

    # ────────────────────────── hashing ──────────────────────────

    def _hash(self, key) -> int:
        """
        Polynomial rolling hash for strings; built-in hash for others.
        Maps key → bucket index.
        """
        if isinstance(key, str):
            h = 0
            prime = 31
            for i, ch in enumerate(key):
                h = (h + ord(ch) * (prime ** i)) % self.capacity
            return h
        return abs(hash(key)) % self.capacity

    # ────────────────────────── insert / update ──────────────────────────

    def put(self, key, value):
        """Insert or update key→value. O(1) average."""
        if self.size / self.capacity >= self.LOAD_FACTOR_THRESHOLD:
            self._resize()

        idx = self._hash(key)
        node = self.buckets[idx]

        # Walk chain — update if key exists
        while node:
            if node.key == key:
                node.value = value
                return
            node = node.next

        # Prepend new node
        new_node = HashNode(key, value)
        new_node.next = self.buckets[idx]
        self.buckets[idx] = new_node
        self.size += 1

    # ────────────────────────── get ──────────────────────────

    def get(self, key):
        """Retrieve value by key. Returns None if not found. O(1) average."""
        idx = self._hash(key)
        node = self.buckets[idx]
        while node:
            if node.key == key:
                return node.value
            node = node.next
        return None

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.put(key, value)

    def __contains__(self, key):
        return self.get(key) is not None

    # ────────────────────────── delete ──────────────────────────

    def delete(self, key) -> bool:
        """Remove key-value pair. Returns True if deleted. O(1) average."""
        idx = self._hash(key)
        node = self.buckets[idx]
        prev = None

        while node:
            if node.key == key:
                if prev:
                    prev.next = node.next
                else:
                    self.buckets[idx] = node.next
                self.size -= 1
                return True
            prev = node
            node = node.next
        return False

    # ────────────────────────── resize ──────────────────────────

    def _resize(self):
        """Double capacity and rehash all entries."""
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [None] * self.capacity
        self.size = 0
        for head in old_buckets:
            node = head
            while node:
                self.put(node.key, node.value)
                node = node.next

    # ────────────────────────── utility ──────────────────────────

    def keys(self):
        """Return all keys."""
        result = []
        for head in self.buckets:
            node = head
            while node:
                result.append(node.key)
                node = node.next
        return result

    def values(self):
        """Return all values."""
        result = []
        for head in self.buckets:
            node = head
            while node:
                result.append(node.value)
                node = node.next
        return result

    def items(self):
        """Return all (key, value) pairs."""
        result = []
        for head in self.buckets:
            node = head
            while node:
                result.append((node.key, node.value))
                node = node.next
        return result

    def __len__(self):
        return self.size

    def load_factor(self):
        return round(self.size / self.capacity, 3)

    def clear(self):
        self.buckets = [None] * self.capacity
        self.size = 0

    def __repr__(self):
        return f"HashMap(size={self.size}, capacity={self.capacity}, load={self.load_factor()})"

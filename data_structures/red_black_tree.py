"""
Red-Black Tree Implementation
Used for: Balanced inventory distribution across warehouses,
          Order tracking by order ID (sorted, efficient insertion/deletion/search in O(log n))
"""

RED = True
BLACK = False


class RBTNode:
    def __init__(self, key, value):
        self.key = key          # order_id or product_id
        self.value = value      # order/inventory dict
        self.color = RED
        self.left = None
        self.right = None
        self.parent = None

    def __repr__(self):
        color = "RED" if self.color == RED else "BLK"
        return f"[{color} | key={self.key}]"


class RedBlackTree:
    """
    Self-balancing BST. All operations guaranteed O(log n).
    Used for:
        - Storing and retrieving orders sorted by order_id
        - Inventory records sorted by product_id per warehouse
    """

    def __init__(self):
        self.NIL = RBTNode(None, None)   # Sentinel nil node
        self.NIL.color = BLACK
        self.root = self.NIL

    # ────────────────────────── rotations ──────────────────────────

    def _left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    # ────────────────────────── insert ──────────────────────────

    def insert(self, key, value):
        """Insert key-value pair. O(log n)."""
        # Check for duplicate key → update value
        existing = self.search(key)
        if existing:
            existing.value = value
            return

        node = RBTNode(key, value)
        node.left = self.NIL
        node.right = self.NIL

        parent = None
        current = self.root

        while current != self.NIL:
            parent = current
            if node.key < current.key:
                current = current.left
            else:
                current = current.right

        node.parent = parent
        if parent is None:
            self.root = node
        elif node.key < parent.key:
            parent.left = node
        else:
            parent.right = node

        if node.parent is None:
            node.color = BLACK
            return
        if node.parent.parent is None:
            return

        self._fix_insert(node)

    def _fix_insert(self, z):
        while z.parent and z.parent.color == RED:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right
                if y.color == RED:                  # Case 1
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.right:         # Case 2
                        z = z.parent
                        self._left_rotate(z)
                    z.parent.color = BLACK          # Case 3
                    z.parent.parent.color = RED
                    self._right_rotate(z.parent.parent)
            else:
                y = z.parent.parent.left
                if y.color == RED:                  # Mirror Case 1
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.left:          # Mirror Case 2
                        z = z.parent
                        self._right_rotate(z)
                    z.parent.color = BLACK          # Mirror Case 3
                    z.parent.parent.color = RED
                    self._left_rotate(z.parent.parent)
        self.root.color = BLACK

    # ────────────────────────── search ──────────────────────────

    def search(self, key):
        """Search by key. Returns node or None. O(log n)."""
        current = self.root
        while current != self.NIL and current.key != key:
            current = current.left if key < current.key else current.right
        return current if current != self.NIL else None

    def search_value(self, key):
        """Returns the value stored at key, or None."""
        node = self.search(key)
        return node.value if node else None

    # ────────────────────────── delete ──────────────────────────

    def _minimum(self, node):
        while node.left != self.NIL:
            node = node.left
        return node

    def _transplant(self, u, v):
        if u.parent is None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def delete(self, key):
        """Delete by key. O(log n)."""
        z = self.search(key)
        if not z:
            return False
        self._delete_node(z)
        return True

    def _delete_node(self, z):
        y = z
        y_original_color = y.color
        if z.left == self.NIL:
            x = z.right
            self._transplant(z, z.right)
        elif z.right == self.NIL:
            x = z.left
            self._transplant(z, z.left)
        else:
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right
            if y.parent == z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        if y_original_color == BLACK:
            self._fix_delete(x)

    def _fix_delete(self, x):
        while x != self.root and x.color == BLACK:
            if x == x.parent.left:
                w = x.parent.right
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self._left_rotate(x.parent)
                    w = x.parent.right
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.right.color == BLACK:
                        w.left.color = BLACK
                        w.color = RED
                        self._right_rotate(w)
                        w = x.parent.right
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.right.color = BLACK
                    self._left_rotate(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self._right_rotate(x.parent)
                    w = x.parent.left
                if w.right.color == BLACK and w.left.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.left.color == BLACK:
                        w.right.color = BLACK
                        w.color = RED
                        self._left_rotate(w)
                        w = x.parent.left
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.left.color = BLACK
                    self._right_rotate(x.parent)
                    x = self.root
        x.color = BLACK

    # ────────────────────────── traversal ──────────────────────────

    def inorder(self):
        """In-order traversal → sorted list of (key, value) tuples."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node != self.NIL:
            self._inorder(node.left, result)
            result.append((node.key, node.value))
            self._inorder(node.right, result)

    def size(self):
        return len(self.inorder())

    def is_empty(self):
        return self.root == self.NIL

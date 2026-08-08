"""
Red-Black Tree (RBT) - Used for:
  - Tracking customer orders and their statuses (O(log n) insert/search/delete)
  - Maintaining sorted order of orders by order_id for efficient retrieval
  - Balancing inventory data across warehouses

Properties:
  1. Every node is RED or BLACK
  2. Root is BLACK
  3. Leaf (NIL) nodes are BLACK
  4. RED node's children are BLACK (no two consecutive reds)
  5. All paths from node to NIL leaves have same number of BLACK nodes
"""

RED = "RED"
BLACK = "BLACK"


class RBTNode:
    def __init__(self, key, value=None):
        self.key = key          # order_id or inventory key
        self.value = value      # order/inventory data dict
        self.color = RED
        self.left = None
        self.right = None
        self.parent = None

    def __repr__(self):
        return f"RBTNode(key={self.key}, color={self.color})"


class RedBlackTree:
    """
    Self-balancing BST guaranteeing O(log n) operations.
    Used here to manage customer orders with status tracking.
    """

    def __init__(self):
        # Sentinel NIL node (BLACK by definition)
        self.NIL = RBTNode(key=None)
        self.NIL.color = BLACK
        self.NIL.left = self.NIL
        self.NIL.right = self.NIL
        self.root = self.NIL

    # -------------------------------------------------------------------------
    # Rotations (maintain BST property while fixing RBT violations)
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # Insert
    # -------------------------------------------------------------------------
    def insert(self, key, value=None):
        """Insert a new key-value pair into the RBT."""
        node = RBTNode(key, value)
        node.left = self.NIL
        node.right = self.NIL

        parent = None
        current = self.root

        while current != self.NIL:
            parent = current
            if node.key < current.key:
                current = current.left
            elif node.key > current.key:
                current = current.right
            else:
                # Key exists → update value
                current.value = value
                return

        node.parent = parent
        if parent is None:
            self.root = node
        elif node.key < parent.key:
            parent.left = node
        else:
            parent.right = node

        node.color = RED
        self._fix_insert(node)

    def _fix_insert(self, z):
        while z.parent and z.parent.color == RED:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right   # uncle
                if y.color == RED:           # Case 1: uncle is RED
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.right:  # Case 2: uncle BLACK, z is right child
                        z = z.parent
                        self._left_rotate(z)
                    z.parent.color = BLACK   # Case 3: uncle BLACK, z is left child
                    z.parent.parent.color = RED
                    self._right_rotate(z.parent.parent)
            else:
                y = z.parent.parent.left    # uncle (mirror)
                if y.color == RED:
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self._right_rotate(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._left_rotate(z.parent.parent)
        self.root.color = BLACK

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------
    def search(self, key):
        """Return node with given key, or None if not found. O(log n)."""
        current = self.root
        while current != self.NIL and current.key is not None:
            if key == current.key:
                return current
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------
    def delete(self, key):
        """Remove node with given key. O(log n)."""
        z = self.search(key)
        if z is None:
            return False
        self._delete_node(z)
        return True

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

    # -------------------------------------------------------------------------
    # Traversal utilities
    # -------------------------------------------------------------------------
    def inorder(self):
        """Return all (key, value) pairs in sorted order."""
        result = []
        self._inorder_helper(self.root, result)
        return result

    def _inorder_helper(self, node, result):
        if node != self.NIL and node.key is not None:
            self._inorder_helper(node.left, result)
            result.append((node.key, node.value))
            self._inorder_helper(node.right, result)

    def update(self, key, new_value):
        """Update the value for an existing key. O(log n)."""
        node = self.search(key)
        if node:
            node.value = new_value
            return True
        return False

    def size(self):
        """Count total nodes."""
        return len(self.inorder())

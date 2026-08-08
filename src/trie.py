"""
Trie (Prefix Tree) - Used for:
  - Fast product search by name or prefix (O(m) where m = query length)
  - Auto-complete / prefix matching on product names
  - Hierarchical category/subcategory representation
  - Outperforms HashMap for prefix-based lookups

Each character of a product name occupies one Trie node.
At the end of each valid product name, is_end_of_word = True
and product_ids stores all SKUs whose name ends here.
"""


class TrieNode:
    def __init__(self):
        self.children = {}          # char → TrieNode
        self.is_end_of_word = False
        self.product_ids = []       # SKUs that end at this node (handles duplicates gracefully)

    def __repr__(self):
        return f"TrieNode(children={list(self.children.keys())}, end={self.is_end_of_word})"


class Trie:
    """
    Prefix tree for O(m) product name searches and autocomplete.
    m = length of the search key / product name.
    """

    def __init__(self):
        self.root = TrieNode()
        self._total_words = 0

    # -------------------------------------------------------------------------
    # Insert
    # -------------------------------------------------------------------------
    def insert(self, product_name: str, product_id: str):
        """
        Insert a product name → product_id mapping.
        Names are stored case-insensitively for user-friendly search.
        """
        name = product_name.lower().strip()
        current = self.root
        for char in name:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]

        if not current.is_end_of_word:
            current.is_end_of_word = True
            self._total_words += 1

        if product_id not in current.product_ids:
            current.product_ids.append(product_id)

    # -------------------------------------------------------------------------
    # Search (exact)
    # -------------------------------------------------------------------------
    def search(self, product_name: str) -> list:
        """
        Exact name search. Returns list of product_ids or [].
        Time: O(m)
        """
        node = self._traverse(product_name)
        if node and node.is_end_of_word:
            return node.product_ids
        return []

    # -------------------------------------------------------------------------
    # Prefix search  (core feature for autocomplete)
    # -------------------------------------------------------------------------
    def starts_with(self, prefix: str) -> list:
        """
        Return all product names (and their IDs) whose name starts with `prefix`.
        Time: O(m + k) where k = number of results
        """
        prefix = prefix.lower().strip()
        node = self._traverse(prefix)
        if node is None:
            return []

        results = []
        self._collect_all(node, prefix, results)
        return results

    def _collect_all(self, node: TrieNode, current_word: str, results: list):
        """DFS to collect all complete words under a node."""
        if node.is_end_of_word:
            results.append((current_word, node.product_ids[:]))
        for char, child in node.children.items():
            self._collect_all(child, current_word + char, results)

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------
    def delete(self, product_name: str, product_id: str = None) -> bool:
        """
        Remove a product_name (and optionally only a specific product_id).
        Returns True if deletion happened.
        """
        name = product_name.lower().strip()
        return self._delete_helper(self.root, name, 0, product_id)

    def _delete_helper(self, node: TrieNode, name: str, depth: int, pid) -> bool:
        if node is None:
            return False

        if depth == len(name):
            if not node.is_end_of_word:
                return False
            if pid and pid in node.product_ids:
                node.product_ids.remove(pid)
            else:
                node.product_ids.clear()

            if not node.product_ids:
                node.is_end_of_word = False
                self._total_words -= 1
            return len(node.children) == 0

        char = name[depth]
        if char not in node.children:
            return False

        should_delete_child = self._delete_helper(node.children[char], name, depth + 1, pid)
        if should_delete_child:
            del node.children[char]
            return not node.is_end_of_word and len(node.children) == 0
        return False

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------
    def _traverse(self, word: str):
        """Walk the trie following `word`; return final node or None."""
        current = self.root
        for char in word.lower().strip():
            if char not in current.children:
                return None
            current = current.children[char]
        return current

    def count_products(self) -> int:
        return self._total_words

    def all_products(self) -> list:
        """Return all (name, [ids]) stored in the trie."""
        results = []
        self._collect_all(self.root, "", results)
        return results

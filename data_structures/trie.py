"""
Trie (Prefix Tree) Implementation
Used for: Fast product name search by prefix / autocomplete suggestions
          Represents hierarchical product category relationships
          Search is O(m) where m = length of search key
"""


class TrieNode:
    def __init__(self):
        self.children = {}          # char → TrieNode
        self.is_end = False         # marks end of a product name
        self.product_ids = []       # all product IDs whose name ends here


class Trie:
    """
    Prefix tree for instant product search.
    - insert(word, product_id)  → O(m)
    - search(word)              → O(m) exact match, returns product_ids
    - starts_with(prefix)       → O(m + k) prefix match, returns all matching product_ids
    - autocomplete(prefix, n)   → top-n suggestions for a prefix
    - delete(word, product_id)  → O(m)
    """

    def __init__(self):
        self.root = TrieNode()

    # ────────────────────────── insert ──────────────────────────

    def insert(self, word: str, product_id: str):
        """Insert a product name and map it to product_id. O(m)."""
        word = word.lower().strip()
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        if product_id not in node.product_ids:
            node.product_ids.append(product_id)

    # ────────────────────────── search ──────────────────────────

    def search(self, word: str):
        """Exact match. Returns list of product_ids or empty list. O(m)."""
        word = word.lower().strip()
        node = self._traverse_to(word)
        if node and node.is_end:
            return node.product_ids
        return []

    def _traverse_to(self, prefix: str):
        """Walk the trie to the end of prefix. Returns node or None."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    # ────────────────────────── prefix search ──────────────────────────

    def starts_with(self, prefix: str):
        """
        Returns all (word, product_ids) pairs whose name starts with prefix.
        O(m + total_chars_in_subtree).
        """
        prefix = prefix.lower().strip()
        node = self._traverse_to(prefix)
        if not node:
            return []
        results = []
        self._collect_all(node, prefix, results)
        return results

    def _collect_all(self, node: TrieNode, current_word: str, results: list):
        """DFS through subtree collecting all complete words."""
        if node.is_end:
            results.append((current_word, node.product_ids))
        for char, child in node.children.items():
            self._collect_all(child, current_word + char, results)

    # ────────────────────────── autocomplete ──────────────────────────

    def autocomplete(self, prefix: str, top_n: int = 5):
        """
        Return up to top_n product name suggestions for a given prefix.
        BFS-based for breadth-first ordering (shorter names first).
        """
        prefix = prefix.lower().strip()
        node = self._traverse_to(prefix)
        if not node:
            return []

        suggestions = []
        # BFS from the prefix node
        queue = [(node, prefix)]
        while queue and len(suggestions) < top_n:
            curr_node, curr_word = queue.pop(0)
            if curr_node.is_end:
                for pid in curr_node.product_ids:
                    suggestions.append((curr_word, pid))
                    if len(suggestions) >= top_n:
                        break
            for char in sorted(curr_node.children.keys()):
                queue.append((curr_node.children[char], curr_word + char))
        return suggestions

    # ────────────────────────── delete ──────────────────────────

    def delete(self, word: str, product_id: str = None):
        """
        Remove a word (or specific product_id mapping) from the trie.
        O(m).
        """
        word = word.lower().strip()
        self._delete_recursive(self.root, word, 0, product_id)

    def _delete_recursive(self, node: TrieNode, word: str, depth: int, product_id):
        if node is None:
            return False

        if depth == len(word):
            if not node.is_end:
                return False
            if product_id and product_id in node.product_ids:
                node.product_ids.remove(product_id)
                if not node.product_ids:
                    node.is_end = False
            else:
                node.is_end = False
                node.product_ids = []
            return len(node.children) == 0

        char = word[depth]
        if char not in node.children:
            return False

        should_delete_child = self._delete_recursive(
            node.children[char], word, depth + 1, product_id
        )
        if should_delete_child:
            del node.children[char]
            return len(node.children) == 0 and not node.is_end
        return False

    # ────────────────────────── helpers ──────────────────────────

    def all_words(self):
        """Return all (word, product_ids) pairs in the trie."""
        results = []
        self._collect_all(self.root, "", results)
        return results

    def count_words(self):
        return len(self.all_words())

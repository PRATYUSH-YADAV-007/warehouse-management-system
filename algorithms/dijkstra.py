"""
Dijkstra's Algorithm — Shortest Path for Warehouse Routing
Used for:
  - Finding the nearest warehouse to a customer (by distance/cost)
  - Optimizing delivery routes between warehouses and customer locations
  - Rerouting shipments when delays occur (port, customs)
  - Determining optimal inventory placement

Graph is represented as an adjacency list: dict[node → list[(neighbor, weight)]]
Nodes can be warehouse IDs or city names.
"""

import heapq


class Graph:
    """
    Weighted directed graph with Dijkstra's shortest-path algorithm.
    Used to model the warehouse-to-customer delivery network.
    """

    def __init__(self):
        # adjacency list: node → list of (neighbor, weight)
        self.adj = {}

    # ────────────────────────── graph building ──────────────────────────

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, u, v, weight: float, bidirectional: bool = True):
        """
        Add an edge between u and v with given weight.
        bidirectional=True for road networks (default).
        """
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append((v, weight))
        if bidirectional:
            self.adj[v].append((u, weight))

    def remove_edge(self, u, v):
        """Remove edge u→v (and v→u if present)."""
        if u in self.adj:
            self.adj[u] = [(n, w) for n, w in self.adj[u] if n != v]
        if v in self.adj:
            self.adj[v] = [(n, w) for n, w in self.adj[v] if n != u]

    def nodes(self):
        return list(self.adj.keys())

    def neighbors(self, node):
        return self.adj.get(node, [])

    # ────────────────────────── Dijkstra's Algorithm ──────────────────────────

    def dijkstra(self, source: str):
        """
        Single-source shortest paths from `source` to all reachable nodes.

        Returns:
            dist  : dict[node → shortest distance from source]
            prev  : dict[node → previous node on shortest path]

        Time complexity: O((V + E) log V) using a min-heap.
        """
        dist = {node: float('inf') for node in self.adj}
        prev = {node: None for node in self.adj}

        if source not in dist:
            return {}, {}

        dist[source] = 0
        # Min-heap: (distance, node)
        heap = [(0, source)]

        while heap:
            current_dist, u = heapq.heappop(heap)

            # Skip if we already found a shorter path
            if current_dist > dist[u]:
                continue

            for v, weight in self.adj.get(u, []):
                new_dist = dist[u] + weight
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    prev[v] = u
                    heapq.heappush(heap, (new_dist, v))

        return dist, prev

    def shortest_path(self, source: str, destination: str):
        """
        Returns (distance, path_list) from source to destination.
        path_list is the ordered list of nodes along the shortest path.
        Returns (inf, []) if no path exists.
        """
        dist, prev = self.dijkstra(source)

        if destination not in dist or dist[destination] == float('inf'):
            return float('inf'), []

        # Reconstruct path by backtracking from destination
        path = []
        current = destination
        while current is not None:
            path.append(current)
            current = prev[current]
        path.reverse()
        return dist[destination], path

    # ────────────────────────── nearest warehouse ──────────────────────────

    def nearest_warehouse_with_stock(
        self, customer_location: str, warehouses: list, stock_checker
    ):
        """
        Finds the nearest warehouse (by Dijkstra distance) that has stock.

        Args:
            customer_location : node name for the customer
            warehouses        : list of warehouse node names to consider
            stock_checker     : callable(warehouse_id) → True if has stock

        Returns:
            (warehouse_id, distance, path) or (None, inf, []) if none found
        """
        if customer_location not in self.adj:
            return None, float('inf'), []

        dist, prev = self.dijkstra(customer_location)

        best_wh = None
        best_dist = float('inf')

        for wh in warehouses:
            if dist.get(wh, float('inf')) < best_dist and stock_checker(wh):
                best_dist = dist[wh]
                best_wh = wh

        if best_wh is None:
            return None, float('inf'), []

        _, path = self.shortest_path(customer_location, best_wh)
        return best_wh, best_dist, path

    def all_reachable(self, source: str):
        """Return all nodes reachable from source with their distances."""
        dist, _ = self.dijkstra(source)
        return {k: v for k, v in dist.items() if v < float('inf')}

    # ────────────────────────── display ──────────────────────────

    def display(self):
        """Print adjacency list (unique edges only for undirected)."""
        print("\n  Delivery Network Graph:")
        seen = set()
        for u in self.adj:
            for v, w in self.adj[u]:
                edge = tuple(sorted([u, v]))
                if edge not in seen:
                    seen.add(edge)
                    print(f"    {u}  ──({w} km)──  {v}")

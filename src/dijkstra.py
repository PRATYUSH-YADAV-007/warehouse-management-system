"""
Dijkstra's Algorithm - Used for:
  - Finding the nearest warehouse with sufficient stock for an order
  - Optimizing delivery routes between warehouses and customers
  - Rerouting shipments around delays (customs, port congestion)
  - In-warehouse path optimization (pick route for workers/robots)

Graph: adjacency list where nodes = warehouse IDs / city hubs
       edge weights = distance (km) or travel time (hrs)

Time Complexity: O((V + E) log V) using a min-heap priority queue
"""

import heapq
from typing import Dict, List, Tuple, Optional


class Graph:
    """
    Weighted undirected graph for the delivery / warehouse network.
    Each node is a warehouse_id or distribution hub.
    Each edge weight represents distance in km.
    """

    def __init__(self):
        # adjacency list: { node: [(neighbor, weight), ...] }
        self.adj: Dict[str, List[Tuple[str, float]]] = {}

    def add_node(self, node: str):
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, u: str, v: str, weight: float):
        """Add a bidirectional edge (undirected graph)."""
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append((v, weight))
        self.adj[v].append((u, weight))

    def remove_edge(self, u: str, v: str):
        """Remove edge in both directions (for rerouting on delays)."""
        if u in self.adj:
            self.adj[u] = [(n, w) for (n, w) in self.adj[u] if n != v]
        if v in self.adj:
            self.adj[v] = [(n, w) for (n, w) in self.adj[v] if n != u]

    def neighbors(self, node: str) -> List[Tuple[str, float]]:
        return self.adj.get(node, [])

    def nodes(self) -> List[str]:
        return list(self.adj.keys())


class Dijkstra:
    """
    Shortest-path finder using Dijkstra's algorithm with a binary min-heap.

    Returns:
      - shortest distances from source to all reachable nodes
      - predecessor map to reconstruct paths
    """

    def __init__(self, graph: Graph):
        self.graph = graph

    def shortest_paths(self, source: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
        """
        Run Dijkstra from `source`.

        Returns:
            dist    : { node: min_distance_from_source }
            prev    : { node: predecessor_node }  (for path reconstruction)
        """
        INF = float('inf')
        dist = {node: INF for node in self.graph.nodes()}
        prev: Dict[str, Optional[str]] = {node: None for node in self.graph.nodes()}

        if source not in dist:
            return {}, {}

        dist[source] = 0
        # min-heap entries: (distance, node)
        heap = [(0, source)]

        visited = set()

        while heap:
            current_dist, u = heapq.heappop(heap)

            if u in visited:
                continue
            visited.add(u)

            for v, weight in self.graph.neighbors(u):
                alt = current_dist + weight
                if alt < dist.get(v, INF):
                    dist[v] = alt
                    prev[v] = u
                    heapq.heappush(heap, (alt, v))

        return dist, prev

    def shortest_path_to(self, source: str, target: str) -> Tuple[float, List[str]]:
        """
        Find the shortest path from source to a single target.

        Returns:
            (distance, [source, ..., target]) or (inf, []) if unreachable.
        """
        dist, prev = self.shortest_paths(source)

        if target not in dist or dist[target] == float('inf'):
            return float('inf'), []

        # Reconstruct path by backtracking through prev
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = prev.get(current)
        path.reverse()

        return dist[target], path

    def nearest_warehouse_with_stock(
        self,
        source: str,
        warehouses_stock: Dict[str, int],
        required_qty: int
    ) -> Tuple[Optional[str], float, List[str]]:
        """
        Find the nearest warehouse (from `source`) that has >= `required_qty` in stock.

        Args:
            source          : customer location / hub node
            warehouses_stock: { warehouse_id: available_stock }
            required_qty    : minimum stock needed

        Returns:
            (best_warehouse_id, distance, path) or (None, inf, []) if none found
        """
        dist, prev = self.shortest_paths(source)

        best_wh = None
        best_dist = float('inf')

        for wh_id, stock in warehouses_stock.items():
            if stock >= required_qty and wh_id in dist:
                if dist[wh_id] < best_dist:
                    best_dist = dist[wh_id]
                    best_wh = wh_id

        if best_wh is None:
            return None, float('inf'), []

        # Reconstruct path to best warehouse
        path = []
        current = best_wh
        while current is not None:
            path.append(current)
            current = prev.get(current)
        path.reverse()

        return best_wh, best_dist, path

    def all_pairs_shortest(self) -> Dict[str, Dict[str, float]]:
        """
        Run Dijkstra from every node. Useful for pre-computing delivery matrices.
        O(V * (V + E) log V)
        """
        result = {}
        for node in self.graph.nodes():
            dist, _ = self.shortest_paths(node)
            result[node] = dist
        return result

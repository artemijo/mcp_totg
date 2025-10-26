#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOTG Core Temporal Graph - Fixed Implementation
==============================================

Production-ready temporal graph with corrected navigation logic.

Key Fixes:
1. Navigation uses graph traversal (BFS), not just direct edges
2. Clear separation of direct vs. reachable nodes
3. Proper error handling
4. English-only documentation
"""

import bisect
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
from enum import Enum


class NodeType(Enum):
    """Types of nodes in temporal graph"""
    CONTENT = "content"
    BRANCH_POINT = "branch"
    MERGE_POINT = "merge"
    MEMORY_COMPRESSED = "memory"


class TemporalRelation(Enum):
    """Types of temporal relationships"""
    SEQUENTIAL = "sequential"
    CAUSAL = "causal"
    CONCURRENT = "concurrent"
    BRANCH = "branch"
    MERGE = "merge"


@dataclass
class TemporalNode:
    """Node in temporal graph"""
    id: str
    timestamp: datetime
    node_type: NodeType
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Indexing
    temporal_index: int = -1
    layer_id: str = ""
    
    def __post_init__(self):
        if self.layer_id == "":
            self.layer_id = self._compute_layer_id()
    
    def _compute_layer_id(self) -> str:
        """Compute temporal layer ID based on timestamp"""
        # Normalize ALL timestamps to UTC without timezone
        timestamp_utc = self._normalize_timestamp(self.timestamp)
        
        days_since_epoch = (timestamp_utc - datetime(1970, 1, 1)).days
        return f"layer_{days_since_epoch // 7}"  # Weekly layers
    
    def _normalize_timestamp(self, timestamp: datetime) -> datetime:
        """Normalize timestamp to UTC without timezone"""
        if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is not None:
            # Convert timezone-aware to UTC without timezone
            return timestamp.astimezone(timezone.utc).replace(tzinfo=None)
        # Assume naive datetimes are already UTC
        return timestamp


@dataclass
class TemporalEdge:
    """Edge in temporal graph"""
    from_node: str
    to_node: str
    relation: TemporalRelation
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TemporalGraph:
    """
    Core Temporal Graph with Fixed Navigation
    
    FIXED: Navigation methods now use proper graph traversal (BFS)
    instead of only checking direct edges.
    """
    
    def __init__(self, layer_duration_days: int = 7):
        self.layer_duration_days = layer_duration_days
        
        # Core storage
        self.nodes: Dict[str, TemporalNode] = {}
        self.edges: Dict[str, List[TemporalEdge]] = defaultdict(list)
        self.reverse_edges: Dict[str, List[TemporalEdge]] = defaultdict(list)
        
        # Time indexing
        self.timestamp_index: List[Tuple[datetime, str]] = []
        self.layers: Dict[str, List[str]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            'nodes_created': 0,
            'edges_created': 0,
            'layers_created': 0,
            'traversals_performed': 0
        }
    
    def _normalize_timestamp(self, timestamp: datetime) -> datetime:
        """Normalize timestamp to UTC without timezone"""
        if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is not None:
            # Convert timezone-aware to UTC without timezone
            return timestamp.astimezone(timezone.utc).replace(tzinfo=None)
        # Assume naive datetimes are already UTC
        return timestamp
    
    def add_node(self, node: TemporalNode) -> bool:
        """
        Add node to temporal graph
        
        Returns:
            True if successfully added
        """
        try:
            self.nodes[node.id] = node
            
            # Update timestamp index (sorted insertion)
            bisect.insort(self.timestamp_index, (node.timestamp, node.id))
            node.temporal_index = len(self.timestamp_index) - 1
            
            # Add to layer
            self.layers[node.layer_id].append(node.id)
            
            self.stats['nodes_created'] += 1
            self.stats['layers_created'] = len(self.layers)
            
            return True
            
        except Exception as e:
            print(f"Error adding node {node.id}: {e}")
            return False
    
    def add_edge(self, edge: TemporalEdge) -> bool:
        """
        Add temporal edge
        
        Returns:
            True if successfully added
        """
        try:
            from_node = self.nodes.get(edge.from_node)
            to_node = self.nodes.get(edge.to_node)
            
            if not from_node or not to_node:
                print(f"Cannot create edge: missing nodes {edge.from_node} -> {edge.to_node}")
                return False
            
            # Validate temporal order for sequential/causal edges
            if edge.relation in [TemporalRelation.SEQUENTIAL, TemporalRelation.CAUSAL]:
                # Normalize both timestamps before comparison
                from_time = self._normalize_timestamp(from_node.timestamp)
                to_time = self._normalize_timestamp(to_node.timestamp)
                if from_time > to_time:
                    print(f"Warning: temporal edge goes backward in time")
            
            # Add to forward and reverse indices
            self.edges[edge.from_node].append(edge)
            self.reverse_edges[edge.to_node].append(edge)
            
            self.stats['edges_created'] += 1
            
            return True
            
        except Exception as e:
            print(f"Error adding edge {edge.from_node} -> {edge.to_node}: {e}")
            return False
    
    # =========================================================================
    # TEMPORAL NAVIGATION - FIXED WITH GRAPH TRAVERSAL
    # =========================================================================
    
    def get_nodes_in_timerange(self, start_time: datetime, end_time: datetime) -> List[str]:
        """
        Get nodes in temporal range using binary search
        
        Complexity: O(log N + K) where K is number of results
        """
        start_pos = bisect.bisect_left(self.timestamp_index, (start_time, ""))
        end_pos = bisect.bisect_right(self.timestamp_index, (end_time, chr(255)*100))
        
        result_ids = [self.timestamp_index[i][1] for i in range(start_pos, end_pos)]
        return result_ids
    
    def get_forward_nodes(self, 
                         node_id: str, 
                         time_window_days: int = 30,
                         max_hops: int = 5,
                         max_results: int = 50) -> List[str]:
        """
        FIXED: Get all reachable future nodes using BFS traversal
        
        This now correctly finds ALL nodes reachable from the source node,
        not just directly connected ones.
        
        Args:
            node_id: Source node ID
            time_window_days: Maximum time window in days
            max_hops: Maximum number of hops in graph traversal
            max_results: Maximum number of results to return
            
        Returns:
            List of reachable future node IDs, sorted by timestamp
        """
        if node_id not in self.nodes:
            return []
        
        source_node = self.nodes[node_id]
        end_time = source_node.timestamp + timedelta(days=time_window_days)
        
        # BFS to find all reachable nodes
        reachable = self._bfs_forward(node_id, max_hops, end_time)
        
        # Filter by time window and exclude source
        future_nodes = []
        for reached_id in reachable:
            if reached_id == node_id:
                continue
            
            reached_node = self.nodes[reached_id]
            if source_node.timestamp < reached_node.timestamp <= end_time:
                future_nodes.append(reached_id)
        
        # Sort by timestamp and limit results
        future_nodes.sort(key=lambda nid: self.nodes[nid].timestamp)
        
        self.stats['traversals_performed'] += 1
        
        return future_nodes[:max_results]
    
    def get_backward_nodes(self, 
                          node_id: str, 
                          time_window_days: int = 30,
                          max_hops: int = 5,
                          max_results: int = 50) -> List[str]:
        """
        FIXED: Get all reachable past nodes using BFS traversal
        
        This now correctly finds ALL nodes that can reach the target node,
        not just directly connected ones.
        
        Args:
            node_id: Target node ID
            time_window_days: Maximum time window in days
            max_hops: Maximum number of hops in graph traversal
            max_results: Maximum number of results to return
            
        Returns:
            List of reachable past node IDs, sorted by timestamp (descending)
        """
        if node_id not in self.nodes:
            return []
        
        target_node = self.nodes[node_id]
        start_time = target_node.timestamp - timedelta(days=time_window_days)
        
        # BFS to find all nodes that can reach target
        reachable = self._bfs_backward(node_id, max_hops, start_time)
        
        # Filter by time window and exclude target
        past_nodes = []
        for reached_id in reachable:
            if reached_id == node_id:
                continue
            
            reached_node = self.nodes[reached_id]
            if start_time <= reached_node.timestamp < target_node.timestamp:
                past_nodes.append(reached_id)
        
        # Sort by timestamp (most recent first)
        past_nodes.sort(key=lambda nid: self.nodes[nid].timestamp, reverse=True)
        
        self.stats['traversals_performed'] += 1
        
        return past_nodes[:max_results]
    
    def _bfs_forward(self, start_node: str, max_hops: int, end_time: datetime) -> Set[str]:
        """
        BFS traversal in forward direction
        
        Returns:
            Set of all reachable node IDs
        """
        visited = set()
        queue = deque([(start_node, 0)])  # (node_id, hop_count)
        
        while queue:
            current_id, hops = queue.popleft()
            
            if current_id in visited or hops > max_hops:
                continue
            
            visited.add(current_id)
            
            # Stop if we've gone beyond time window
            if current_id in self.nodes:
                current_node = self.nodes[current_id]
                if current_node.timestamp > end_time:
                    continue
            
            # Add neighbors
            for edge in self.edges.get(current_id, []):
                if edge.to_node not in visited:
                    queue.append((edge.to_node, hops + 1))
        
        return visited
    
    def _bfs_backward(self, target_node: str, max_hops: int, start_time: datetime) -> Set[str]:
        """
        BFS traversal in backward direction
        
        Returns:
            Set of all nodes that can reach target
        """
        visited = set()
        queue = deque([(target_node, 0)])  # (node_id, hop_count)
        
        while queue:
            current_id, hops = queue.popleft()
            
            if current_id in visited or hops > max_hops:
                continue
            
            visited.add(current_id)
            
            # Stop if we've gone before time window
            if current_id in self.nodes:
                current_node = self.nodes[current_id]
                if current_node.timestamp < start_time:
                    continue
            
            # Add predecessors
            for edge in self.reverse_edges.get(current_id, []):
                if edge.from_node not in visited:
                    queue.append((edge.from_node, hops + 1))
        
        return visited
    
    # =========================================================================
    # DIRECT CONNECTION METHODS (for when you actually want direct edges)
    # =========================================================================
    
    def get_direct_successors(self, node_id: str) -> List[str]:
        """Get nodes with direct edges FROM this node"""
        return [edge.to_node for edge in self.edges.get(node_id, [])]
    
    def get_direct_predecessors(self, node_id: str) -> List[str]:
        """Get nodes with direct edges TO this node"""
        return [edge.from_node for edge in self.reverse_edges.get(node_id, [])]
    
    def has_edge(self, from_node: str, to_node: str) -> bool:
        """Check if direct edge exists"""
        for edge in self.edges.get(from_node, []):
            if edge.to_node == to_node:
                return True
        return False
    
    def has_path(self, from_node: str, to_node: str, max_hops: int = 10) -> bool:
        """Check if path exists between nodes (using BFS)"""
        if from_node not in self.nodes or to_node not in self.nodes:
            return False
        
        if from_node == to_node:
            return True
        
        visited = set()
        queue = deque([(from_node, 0)])
        
        while queue:
            current_id, hops = queue.popleft()
            
            if current_id == to_node:
                return True
            
            if current_id in visited or hops > max_hops:
                continue
            
            visited.add(current_id)
            
            for edge in self.edges.get(current_id, []):
                if edge.to_node not in visited:
                    queue.append((edge.to_node, hops + 1))
        
        return False
    
    def get_shortest_path(self, from_node: str, to_node: str, max_hops: int = 10) -> Optional[List[str]]:
        """
        Find shortest path between nodes using BFS
        
        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        if from_node not in self.nodes or to_node not in self.nodes:
            return None
        
        if from_node == to_node:
            return [from_node]
        
        visited = set()
        queue = deque([(from_node, [from_node], 0)])  # (current, path, hops)
        
        while queue:
            current_id, path, hops = queue.popleft()
            
            if current_id == to_node:
                return path
            
            if current_id in visited or hops > max_hops:
                continue
            
            visited.add(current_id)
            
            for edge in self.edges.get(current_id, []):
                if edge.to_node not in visited:
                    new_path = path + [edge.to_node]
                    queue.append((edge.to_node, new_path, hops + 1))
        
        return None
    
    # =========================================================================
    # LAYER OPERATIONS
    # =========================================================================
    
    def get_layer_nodes(self, layer_id: str) -> List[str]:
        """Get nodes in specific temporal layer"""
        return self.layers.get(layer_id, []).copy()
    
    def get_adjacent_layers(self, layer_id: str) -> List[str]:
        """Get adjacent temporal layers"""
        try:
            week_num = int(layer_id.split('_')[1])
            
            adjacent = []
            if week_num > 0:
                adjacent.append(f"layer_{week_num-1}")
            adjacent.append(f"layer_{week_num+1}")
            
            return [layer for layer in adjacent if layer in self.layers]
            
        except (IndexError, ValueError):
            return []
    
    # =========================================================================
    # STATISTICS AND DEBUG
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            **self.stats,
            'total_nodes': len(self.nodes),
            'total_edges': sum(len(edges) for edges in self.edges.values()),
            'total_layers': len(self.layers),
            'avg_edges_per_node': self.stats['edges_created'] / max(1, self.stats['nodes_created']),
            'avg_layer_size': len(self.nodes) / max(1, len(self.layers))
        }
    
    def print_summary(self):
        """Print graph summary"""
        stats = self.get_statistics()
        
        print("=" * 70)
        print("TOTG TEMPORAL GRAPH SUMMARY")
        print("=" * 70)
        print(f"Total Nodes:        {stats['total_nodes']}")
        print(f"Total Edges:        {stats['total_edges']}")
        print(f"Total Layers:       {stats['total_layers']}")
        print(f"Avg Edges/Node:     {stats['avg_edges_per_node']:.2f}")
        print(f"Avg Layer Size:     {stats['avg_layer_size']:.2f}")
        print(f"Traversals Done:    {stats['traversals_performed']}")
        
        if self.timestamp_index:
            first_time = self.timestamp_index[0][0]
            last_time = self.timestamp_index[-1][0]
            time_span = last_time - first_time
            print(f"Time Span:          {time_span.days} days")
        
        print("=" * 70)


# =============================================================================
# TESTS
# =============================================================================

def test_fixed_navigation():
    """Test that navigation now works correctly with graph traversal"""
    print("Testing FIXED Navigation with Graph Traversal...")
    print("=" * 70)
    
    graph = TemporalGraph()
    base_time = datetime(2024, 1, 1)
    
    # Create chain: 0 -> 1 -> 2 -> 3 -> 4
    for i in range(5):
        node = TemporalNode(
            id=f"node_{i}",
            timestamp=base_time + timedelta(days=i),
            node_type=NodeType.CONTENT,
            content=f"Content {i}"
        )
        graph.add_node(node)
    
    # Create edges (chain)
    for i in range(4):
        edge = TemporalEdge(
            from_node=f"node_{i}",
            to_node=f"node_{i+1}",
            relation=TemporalRelation.SEQUENTIAL
        )
        graph.add_edge(edge)
    
    print("\nTest 1: Forward Navigation (should find ALL reachable nodes)")
    forward = graph.get_forward_nodes("node_0", time_window_days=10)
    print(f"From node_0, reachable future nodes: {forward}")
    print(f"Expected: ['node_1', 'node_2', 'node_3', 'node_4']")
    print(f"Result: {'✓ PASS' if len(forward) == 4 else '✗ FAIL'}")
    
    print("\nTest 2: Backward Navigation (should find ALL nodes that can reach target)")
    backward = graph.get_backward_nodes("node_4", time_window_days=10)
    print(f"To node_4, reachable past nodes: {backward}")
    print(f"Expected: ['node_3', 'node_2', 'node_1', 'node_0']")
    print(f"Result: {'✓ PASS' if len(backward) == 4 else '✗ FAIL'}")
    
    print("\nTest 3: Path Finding")
    path = graph.get_shortest_path("node_0", "node_4")
    print(f"Shortest path from node_0 to node_4: {path}")
    print(f"Expected: ['node_0', 'node_1', 'node_2', 'node_3', 'node_4']")
    print(f"Result: {'✓ PASS' if path and len(path) == 5 else '✗ FAIL'}")
    
    print("\nTest 4: Direct vs. Reachable")
    direct = graph.get_direct_successors("node_0")
    reachable = graph.get_forward_nodes("node_0", time_window_days=10)
    print(f"Direct successors of node_0: {direct}")
    print(f"All reachable from node_0: {reachable}")
    print(f"Result: {'✓ PASS - They differ as expected!' if len(direct) < len(reachable) else '✗ FAIL'}")
    
    graph.print_summary()
    
    return graph


if __name__ == "__main__":
    test_fixed_navigation()

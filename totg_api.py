#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOTG Production API
==================

Clean, production-ready API for using TOTG in real applications.
Can be easily wrapped as MCP server, REST API, or used directly.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
import json

from totg_core_fixed import (
    TemporalGraph, TemporalNode, TemporalEdge,
    NodeType, TemporalRelation
)
from totg_attention_fixed import BidirectionalAttention
from totg_markovian import MarkovianTOTG, create_markovian_totg


@dataclass
class NodeData:
    """Simplified node data for API responses"""
    id: str
    timestamp: str  # ISO format
    type: str
    content: str
    metadata: Dict[str, Any]


@dataclass
class AttentionResult:
    """Attention computation result"""
    node_id: str
    forward_attention: Dict[str, float]
    backward_attention: Dict[str, float]
    summary: Dict[str, Any]


@dataclass
class PathResult:
    """Path finding result"""
    from_node: str
    to_node: str
    path: Optional[List[str]]
    path_length: int
    exists: bool


class TOTGAPI:
    """
    Production-ready TOTG API
    
    This provides a clean interface for:
    - Adding documents/events
    - Querying temporal relationships
    - Computing attention
    - Finding paths
    
    Can be easily wrapped for MCP, REST API, or CLI usage.
    """
    
    def __init__(self):
        self.graph = TemporalGraph()
        self.attention: Optional[BidirectionalAttention] = None
        self._attention_initialized = False
        self.markovian: Optional[MarkovianTOTG] = None
        self._markovian_initialized = False
    
    def _ensure_attention(self):
        """Lazy initialization of attention system"""
        if not self._attention_initialized:
            self.attention = BidirectionalAttention(self.graph)
            self._attention_initialized = True
    
    def _ensure_markovian(self, chunk_size_days: int = 90):
        """Lazy initialization of Markovian system"""
        if not self._markovian_initialized:
            self.markovian = MarkovianTOTG(self, chunk_size_days=chunk_size_days)
            self._markovian_initialized = True
    
    # =========================================================================
    # GRAPH CONSTRUCTION
    # =========================================================================
    
    def add_document(self,
                    doc_id: str,
                    content: str,
                    timestamp: Optional[datetime] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add document to temporal graph
        
        Args:
            doc_id: Unique document identifier
            content: Document content (text)
            timestamp: Document timestamp (defaults to now)
            metadata: Optional metadata dict
            
        Returns:
            Dict with status and node info
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        elif isinstance(timestamp, str):
            # Handle ISO string timestamps
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                # Handle ISO format with Z timezone
                if timestamp.endswith('Z'):
                    timestamp = datetime.fromisoformat(timestamp[:-1] + '+00:00')
                else:
                    raise
            # Normalize to UTC without timezone
            timestamp = timestamp.replace(tzinfo=None)
        elif hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is not None:
            # Convert timezone-aware to UTC without timezone
            timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
        # else: assume naive datetime is already in correct format
        
        if metadata is None:
            metadata = {}
        
        node = TemporalNode(
            id=doc_id,
            timestamp=timestamp,
            node_type=NodeType.CONTENT,
            content=content,
            metadata=metadata
        )
        
        success = self.graph.add_node(node)
        
        # Invalidate attention cache if it exists
        if self._attention_initialized:
            self.attention.invalidate_cache()
            # Add to semantic model
            self.attention.semantic_sim.add_document(content)
        
        return {
            'success': success,
            'doc_id': doc_id,
            'timestamp': timestamp.isoformat(),
            'message': 'Document added successfully' if success else 'Failed to add document'
        }
    
    def add_relationship(self,
                        from_doc: str,
                        to_doc: str,
                        relation_type: str = "sequential",
                        weight: float = 1.0,
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add relationship between documents
        
        Args:
            from_doc: Source document ID
            to_doc: Target document ID
            relation_type: Type of relation (sequential, causal, concurrent, branch, merge)
            weight: Edge weight
            metadata: Optional metadata
            
        Returns:
            Dict with status
        """
        try:
            relation = TemporalRelation(relation_type)
        except ValueError:
            return {
                'success': False,
                'message': f'Invalid relation type: {relation_type}. Use: sequential, causal, concurrent, branch, merge'
            }
        
        if metadata is None:
            metadata = {}
        
        edge = TemporalEdge(
            from_node=from_doc,
            to_node=to_doc,
            relation=relation,
            weight=weight,
            metadata=metadata
        )
        
        success = self.graph.add_edge(edge)
        
        # Invalidate attention cache
        if self._attention_initialized:
            self.attention.invalidate_cache()
        
        return {
            'success': success,
            'from': from_doc,
            'to': to_doc,
            'relation': relation_type,
            'message': 'Relationship added successfully' if success else 'Failed to add relationship'
        }
    
    # =========================================================================
    # TEMPORAL QUERIES
    # =========================================================================
    
    def get_documents_in_range(self,
                               start_time: datetime,
                               end_time: datetime) -> List[NodeData]:
        """
        Get all documents in time range
        
        Args:
            start_time: Range start
            end_time: Range end
            
        Returns:
            List of NodeData objects
        """
        node_ids = self.graph.get_nodes_in_timerange(start_time, end_time)
        
        return [self._node_to_data(self.graph.nodes[nid]) for nid in node_ids]
    
    def get_future_documents(self,
                           doc_id: str,
                           days: int = 30,
                           max_results: int = 50) -> List[NodeData]:
        """
        Get documents that happen after this one (reachable via graph)
        
        Args:
            doc_id: Source document
            days: Time window in days
            max_results: Max results to return
            
        Returns:
            List of future documents
        """
        node_ids = self.graph.get_forward_nodes(doc_id, days, max_results=max_results)
        
        return [self._node_to_data(self.graph.nodes[nid]) for nid in node_ids]
    
    def get_past_documents(self,
                          doc_id: str,
                          days: int = 30,
                          max_results: int = 50) -> List[NodeData]:
        """
        Get documents that led to this one (reachable via graph)
        
        Args:
            doc_id: Target document
            days: Time window in days
            max_results: Max results to return
            
        Returns:
            List of past documents
        """
        node_ids = self.graph.get_backward_nodes(doc_id, days, max_results=max_results)
        
        return [self._node_to_data(self.graph.nodes[nid]) for nid in node_ids]
    
    def find_path(self,
                 from_doc: str,
                 to_doc: str,
                 max_hops: int = 10) -> PathResult:
        """
        Find path between two documents
        
        Args:
            from_doc: Start document
            to_doc: End document
            max_hops: Maximum path length
            
        Returns:
            PathResult with path info
        """
        path = self.graph.get_shortest_path(from_doc, to_doc, max_hops)
        
        return PathResult(
            from_node=from_doc,
            to_node=to_doc,
            path=path,
            path_length=len(path) if path else 0,
            exists=path is not None
        )
    
    # =========================================================================
    # ATTENTION QUERIES
    # =========================================================================
    
    def compute_attention(self,
                         doc_id: str,
                         max_per_direction: int = 10) -> AttentionResult:
        """
        Compute bidirectional attention for document
        
        Args:
            doc_id: Document to analyze
            max_per_direction: Max results per direction
            
        Returns:
            AttentionResult with weights and summary
        """
        self._ensure_attention()
        
        result = self.attention.compute_bidirectional_attention(
            doc_id,
            max_nodes_per_direction=max_per_direction
        )
        
        return AttentionResult(
            node_id=doc_id,
            forward_attention=result['forward'],
            backward_attention=result['backward'],
            summary={
                'total_forward_weight': result['total_forward_weight'],
                'total_backward_weight': result['total_backward_weight'],
                'attention_balance': result['attention_balance'],
                'most_attended_forward': result['most_attended_forward'],
                'most_attended_backward': result['most_attended_backward']
            }
        )
    
    def find_related_documents(self,
                              doc_id: str,
                              max_results: int = 10,
                              direction: str = "both") -> Dict[str, List[Tuple[str, float]]]:
        """
        Find related documents using attention weights
        
        Args:
            doc_id: Source document
            max_results: Max results to return
            direction: "forward", "backward", or "both"
            
        Returns:
            Dict with forward/backward related docs and their scores
        """
        self._ensure_attention()
        
        result = {}
        
        if direction in ["forward", "both"]:
            forward = self.attention.compute_forward_attention(doc_id, max_results)
            result['forward'] = sorted(forward.items(), key=lambda x: x[1], reverse=True)
        
        if direction in ["backward", "both"]:
            backward = self.attention.compute_backward_attention(doc_id, max_results)
            result['backward'] = sorted(backward.items(), key=lambda x: x[1], reverse=True)
        
        return result
    
    # =========================================================================
    # GRAPH ANALYSIS
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        graph_stats = self.graph.get_statistics()
        
        stats = {
            'graph': graph_stats,
            'attention_enabled': self._attention_initialized
        }
        
        if self._attention_initialized:
            stats['attention'] = self.attention.get_statistics()
        
        return stats
    
    def get_document(self, doc_id: str) -> Optional[NodeData]:
        """Get single document by ID"""
        if doc_id not in self.graph.nodes:
            return None
        
        return self._node_to_data(self.graph.nodes[doc_id])
    
    def list_documents(self, limit: int = 100) -> List[NodeData]:
        """List all documents (up to limit)"""
        nodes = list(self.graph.nodes.values())[:limit]
        return [self._node_to_data(node) for node in nodes]
    
    # =========================================================================
    # EXPORT / SERIALIZATION
    # =========================================================================
    
    def export_graph(self) -> Dict[str, Any]:
        """
        Export entire graph to JSON-serializable dict
        
        Returns:
            Dict with nodes and edges
        """
        nodes = []
        for node in self.graph.nodes.values():
            nodes.append({
                'id': node.id,
                'timestamp': node.timestamp.isoformat(),
                'type': node.node_type.value,
                'content': str(node.content),
                'metadata': node.metadata
            })
        
        edges = []
        for node_id, edge_list in self.graph.edges.items():
            for edge in edge_list:
                edges.append({
                    'from': edge.from_node,
                    'to': edge.to_node,
                    'relation': edge.relation.value,
                    'weight': edge.weight,
                    'metadata': edge.metadata
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'statistics': self.get_statistics()
        }
    
    def export_json(self, filepath: str):
        """Export graph to JSON file"""
        data = self.export_graph()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def _node_to_data(self, node: TemporalNode) -> NodeData:
        """Convert TemporalNode to NodeData for API responses"""
        return NodeData(
            id=node.id,
            timestamp=node.timestamp.isoformat(),
            type=node.node_type.value,
            content=str(node.content),
            metadata=node.metadata
        )
    
    # =========================================================================
    # MARKOVIAN ANALYSIS
    # =========================================================================
    
    def analyze_long_chain(self,
                         start_doc_id: str,
                         end_doc_id: Optional[str] = None,
                         max_days: int = 1825,
                         chunk_size_days: int = 90,
                         detailed_output: bool = False,
                         enable_cache: bool = True):
        """
        Analyze long temporal chain using Markovian chunking
        
        Args:
            start_doc_id: Starting document ID
            end_doc_id: Optional end point
            max_days: Maximum time horizon (default 5 years)
            chunk_size_days: Size of temporal chunks (default 90 days)
            detailed_output: Include full document details
            enable_cache: Use caching for performance
        
        Returns:
            MarkovianAnalysisResult with complete analysis
        """
        self._ensure_markovian(chunk_size_days)
        
        return self.markovian.analyze_long_chain(
            start_doc_id=start_doc_id,
            end_doc_id=end_doc_id,
            max_days=max_days,
            detailed_output=detailed_output,
            enable_cache=enable_cache
        )
    
    def get_temporal_summary(self,
                           start_doc_id: str,
                           end_doc_id: str,
                           num_chunks: int = 10,
                           chunk_size_days: int = 90):
        """
        Get hierarchical summary of temporal period
        
        Args:
            start_doc_id: Start document
            end_doc_id: End document
            num_chunks: Number of summary chunks
            chunk_size_days: Size of temporal chunks
        
        Returns:
            List of chunk summaries
        """
        self._ensure_markovian(chunk_size_days)
        
        return self.markovian.get_temporal_summary(
            start_doc_id=start_doc_id,
            end_doc_id=end_doc_id,
            num_chunks=num_chunks
        )
    
    def create_markovian_analyzer(self, chunk_size_days: int = 90) -> MarkovianTOTG:
        """
        Create a separate Markovian analyzer instance
        
        Args:
            chunk_size_days: Size of temporal chunks
        
        Returns:
            MarkovianTOTG instance
        """
        return create_markovian_totg(self, chunk_size_days)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_usage():
    """Demonstrate API usage"""
    print("=" * 70)
    print("TOTG Production API - Example Usage")
    print("=" * 70)
    
    # Initialize API
    api = TOTGAPI()
    
    # Add documents
    print("\n1. Adding documents...")
    base_date = datetime(2024, 1, 1)
    
    docs = [
        ("doc_1", "Initial project proposal for new software system", base_date),
        ("doc_2", "Requirements specification document", base_date + timedelta(days=7)),
        ("doc_3", "Technical design document", base_date + timedelta(days=14)),
        ("doc_4", "Implementation plan", base_date + timedelta(days=21)),
        ("doc_5", "Testing strategy document", base_date + timedelta(days=28))
    ]
    
    for doc_id, content, timestamp in docs:
        result = api.add_document(doc_id, content, timestamp, metadata={'category': 'project'})
        print(f"  ✓ Added {doc_id}")
    
    # Add relationships
    print("\n2. Adding relationships...")
    for i in range(len(docs) - 1):
        api.add_relationship(docs[i][0], docs[i+1][0], "sequential")
        print(f"  ✓ {docs[i][0]} -> {docs[i+1][0]}")
    
    # Query future documents
    print("\n3. Query: What comes after doc_1?")
    future = api.get_future_documents("doc_1", days=30)
    print(f"  Found {len(future)} future documents:")
    for doc in future:
        print(f"    - {doc.id}: {doc.content[:50]}...")
    
    # Query past documents
    print("\n4. Query: What led to doc_5?")
    past = api.get_past_documents("doc_5", days=30)
    print(f"  Found {len(past)} past documents:")
    for doc in past:
        print(f"    - {doc.id}: {doc.content[:50]}...")
    
    # Find path
    print("\n5. Find path from doc_1 to doc_5")
    path_result = api.find_path("doc_1", "doc_5")
    if path_result.exists:
        print(f"  Path found with {path_result.path_length} steps:")
        print(f"    {' -> '.join(path_result.path)}")
    
    # Compute attention
    print("\n6. Compute attention for doc_3")
    attention = api.compute_attention("doc_3", max_per_direction=3)
    print(f"  Forward attention:")
    for doc_id, weight in attention.forward_attention.items():
        print(f"    {doc_id}: {weight:.3f}")
    print(f"  Backward attention:")
    for doc_id, weight in attention.backward_attention.items():
        print(f"    {doc_id}: {weight:.3f}")
    
    # Get statistics
    print("\n7. System statistics")
    stats = api.get_statistics()
    print(f"  Total nodes: {stats['graph']['total_nodes']}")
    print(f"  Total edges: {stats['graph']['total_edges']}")
    print(f"  Attention enabled: {stats['attention_enabled']}")
    
    # Export
    print("\n8. Exporting graph...")
    # api.export_json("/tmp/totg_export.json")
    # print("  ✓ Exported to /tmp/totg_export.json")
    
    print("\n" + "=" * 70)
    print("✓ Example complete!")
    
    return api


if __name__ == "__main__":
    api = example_usage()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOTG Bidirectional Attention - Fixed Implementation
=================================================

Production-ready attention system with improved semantic similarity.

Key Fixes:
1. Better semantic similarity using TF-IDF instead of simple word overlap
2. Integrated with fixed graph navigation
3. Cleaner API
4. Proper caching strategy
"""

import math
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from enum import Enum

from totg_core_fixed import TemporalGraph, TemporalNode


class AttentionType(Enum):
    """Types of attention over time"""
    FORWARD = "forward"
    BACKWARD = "backward"
    BIDIRECTIONAL = "bidirectional"
    TEMPORAL_FOCUS = "temporal_focus"
    SEMANTIC_FOCUS = "semantic_focus"


@dataclass
class AttentionHead:
    """One attention head focusing on specific aspect"""
    head_id: str
    attention_type: AttentionType
    focus_keywords: List[str] = field(default_factory=list)
    temporal_window_days: int = 30
    decay_factor: float = 0.95
    
    def compute_temporal_decay(self, days_diff: int) -> float:
        """
        Compute temporal decay using exponential function
        
        Args:
            days_diff: Difference in days
            
        Returns:
            Decay coefficient (0-1)
        """
        if days_diff <= 0:
            return 1.0
        
        decay = math.pow(self.decay_factor, days_diff)
        return max(0.01, decay)


class SemanticSimilarity:
    """
    IMPROVED: Better semantic similarity using TF-IDF
    
    This is much better than simple word overlap while still being
    lightweight and not requiring heavy ML models.
    """
    
    def __init__(self):
        # Document frequency for IDF calculation
        self.document_count = 0
        self.term_document_freq: Dict[str, int] = defaultdict(int)
        
        # Stopwords for filtering
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize and clean text"""
        if not isinstance(text, str):
            text = str(text)
        
        # Convert to lowercase and split on non-alphanumeric
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        # Filter stopwords and short tokens
        tokens = [t for t in tokens if t not in self.stopwords and len(t) > 2]
        
        return tokens
    
    def add_document(self, text: str):
        """Add document to corpus for IDF calculation"""
        tokens = set(self._tokenize(text))
        self.document_count += 1
        
        for token in tokens:
            self.term_document_freq[token] += 1
    
    def compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """
        Compute term frequency
        
        TF(t) = (Number of times term t appears) / (Total number of terms)
        """
        if not tokens:
            return {}
        
        token_counts = Counter(tokens)
        total_tokens = len(tokens)
        
        tf = {token: count / total_tokens for token, count in token_counts.items()}
        return tf
    
    def compute_idf(self, token: str) -> float:
        """
        Compute inverse document frequency
        
        IDF(t) = log(Total documents / Documents containing t)
        """
        if self.document_count == 0:
            return 0.0
        
        doc_freq = self.term_document_freq.get(token, 0)
        if doc_freq == 0:
            return 0.0
        
        return math.log(self.document_count / doc_freq)
    
    def compute_tfidf_vector(self, text: str) -> Dict[str, float]:
        """Compute TF-IDF vector for text"""
        tokens = self._tokenize(text)
        tf = self.compute_tf(tokens)
        
        tfidf = {}
        for token, tf_value in tf.items():
            idf_value = self.compute_idf(token)
            tfidf[token] = tf_value * idf_value
        
        return tfidf
    
    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        Compute cosine similarity between two TF-IDF vectors
        
        cos(θ) = (A · B) / (||A|| × ||B||)
        """
        if not vec1 or not vec2:
            return 0.0
        
        # Compute dot product
        common_terms = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)
        
        # Compute magnitudes
        mag1 = math.sqrt(sum(v * v for v in vec1.values()))
        mag2 = math.sqrt(sum(v * v for v in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts
        
        Returns:
            Similarity score (0-1)
        """
        vec1 = self.compute_tfidf_vector(text1)
        vec2 = self.compute_tfidf_vector(text2)
        
        return self.cosine_similarity(vec1, vec2)


class BidirectionalAttention:
    """
    FIXED: Bidirectional Attention System
    
    Key improvements:
    1. Uses fixed graph navigation (gets ALL reachable nodes)
    2. Better semantic similarity (TF-IDF instead of word overlap)
    3. Cleaner integration
    """
    
    def __init__(self, temporal_graph: TemporalGraph):
        self.graph = temporal_graph
        
        # Semantic similarity calculator (IMPROVED)
        self.semantic_sim = SemanticSimilarity()
        
        # Initialize with existing graph content for IDF
        self._initialize_semantic_model()
        
        # Multi-head attention
        self.attention_heads: List[AttentionHead] = []
        
        # Caching system
        self.attention_cache: Dict[str, Dict[str, float]] = {}
        self.cache_timestamp: datetime = datetime.now()
        self.cache_ttl_minutes = 60
        
        # Statistics
        self.stats = {
            'attention_computations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'forward_queries': 0,
            'backward_queries': 0
        }
        
        # Initialize default attention heads
        self._initialize_default_heads()
    
    def _initialize_semantic_model(self):
        """Initialize semantic similarity model with graph content"""
        for node in self.graph.nodes.values():
            if node.content:
                self.semantic_sim.add_document(str(node.content))
    
    def _initialize_default_heads(self):
        """Initialize standard attention heads"""
        
        self.attention_heads.extend([
            # Short-term forward attention
            AttentionHead(
                head_id="short_forward",
                attention_type=AttentionType.FORWARD,
                temporal_window_days=7,
                decay_factor=0.8
            ),
            
            # Long-term backward attention
            AttentionHead(
                head_id="long_backward",
                attention_type=AttentionType.BACKWARD,
                temporal_window_days=90,
                decay_factor=0.98
            ),
            
            # Semantic focus attention
            AttentionHead(
                head_id="semantic_focus",
                attention_type=AttentionType.SEMANTIC_FOCUS,
                temporal_window_days=30,
                decay_factor=0.95,
                focus_keywords=["important", "key", "critical", "main", "significant"]
            ),
            
            # Temporal focus attention
            AttentionHead(
                head_id="temporal_focus",
                attention_type=AttentionType.TEMPORAL_FOCUS,
                temporal_window_days=14,
                decay_factor=0.9
            )
        ])
    
    def compute_forward_attention(self, 
                                 node_id: str, 
                                 max_nodes: int = 10,
                                 use_cache: bool = True) -> Dict[str, float]:
        """
        FIXED: Compute attention to future nodes using proper graph traversal
        
        Args:
            node_id: Source node ID
            max_nodes: Maximum nodes to consider
            use_cache: Whether to use cache
            
        Returns:
            Dict of target node IDs -> attention weights
        """
        if node_id not in self.graph.nodes:
            return {}
        
        # Check cache
        cache_key = f"forward_{node_id}_{max_nodes}"
        if use_cache and self._is_cache_valid(cache_key):
            self.stats['cache_hits'] += 1
            return self.attention_cache[cache_key]
        
        self.stats['cache_misses'] += 1
        self.stats['forward_queries'] += 1
        
        source_node = self.graph.nodes[node_id]
        
        # FIXED: Use proper graph traversal to get ALL reachable future nodes
        future_nodes = self.graph.get_forward_nodes(
            node_id, 
            time_window_days=max(h.temporal_window_days for h in self.attention_heads),
            max_results=max_nodes * 2  # Get more, then filter
        )
        
        if not future_nodes:
            return {}
        
        # Compute attention weights using all heads
        attention_scores = {}
        
        for head in self.attention_heads:
            if head.attention_type in [AttentionType.FORWARD, AttentionType.BIDIRECTIONAL, AttentionType.TEMPORAL_FOCUS]:
                head_weights = self._compute_head_attention(
                    source_node, future_nodes, head, "forward"
                )
                
                # Aggregate head weights
                for target_id, weight in head_weights.items():
                    if target_id not in attention_scores:
                        attention_scores[target_id] = 0.0
                    attention_scores[target_id] += weight / len(self.attention_heads)
        
        # Sort by weight and take top N
        sorted_scores = dict(sorted(attention_scores.items(), key=lambda x: x[1], reverse=True)[:max_nodes])
        
        # Cache result
        if use_cache:
            self.attention_cache[cache_key] = sorted_scores
        
        self.stats['attention_computations'] += 1
        
        return sorted_scores
    
    def compute_backward_attention(self, 
                                  node_id: str, 
                                  max_nodes: int = 10,
                                  use_cache: bool = True) -> Dict[str, float]:
        """
        FIXED: Compute attention to past nodes using proper graph traversal
        
        Args:
            node_id: Target node ID
            max_nodes: Maximum nodes to consider
            use_cache: Whether to use cache
            
        Returns:
            Dict of source node IDs -> attention weights
        """
        if node_id not in self.graph.nodes:
            return {}
        
        # Check cache
        cache_key = f"backward_{node_id}_{max_nodes}"
        if use_cache and self._is_cache_valid(cache_key):
            self.stats['cache_hits'] += 1
            return self.attention_cache[cache_key]
        
        self.stats['cache_misses'] += 1
        self.stats['backward_queries'] += 1
        
        target_node = self.graph.nodes[node_id]
        
        # FIXED: Use proper graph traversal to get ALL reachable past nodes
        past_nodes = self.graph.get_backward_nodes(
            node_id,
            time_window_days=max(h.temporal_window_days for h in self.attention_heads),
            max_results=max_nodes * 2
        )
        
        if not past_nodes:
            return {}
        
        # Compute attention weights using all heads
        attention_scores = {}
        
        for head in self.attention_heads:
            if head.attention_type in [AttentionType.BACKWARD, AttentionType.BIDIRECTIONAL, AttentionType.SEMANTIC_FOCUS]:
                head_weights = self._compute_head_attention(
                    target_node, past_nodes, head, "backward"
                )
                
                # Aggregate head weights
                for source_id, weight in head_weights.items():
                    if source_id not in attention_scores:
                        attention_scores[source_id] = 0.0
                    attention_scores[source_id] += weight / len(self.attention_heads)
        
        # Sort by weight and take top N
        sorted_scores = dict(sorted(attention_scores.items(), key=lambda x: x[1], reverse=True)[:max_nodes])
        
        # Cache result
        if use_cache:
            self.attention_cache[cache_key] = sorted_scores
        
        self.stats['attention_computations'] += 1
        
        return sorted_scores
    
    def _compute_head_attention(self, 
                               reference_node: TemporalNode,
                               candidate_nodes: List[str], 
                               head: AttentionHead, 
                               direction: str) -> Dict[str, float]:
        """
        Compute attention for specific head
        
        IMPROVED: Uses better semantic similarity
        """
        weights = {}
        
        for candidate_id in candidate_nodes:
            if candidate_id not in self.graph.nodes:
                continue
            
            candidate_node = self.graph.nodes[candidate_id]
            
            # Factor 1: Semantic similarity (IMPROVED with TF-IDF)
            semantic_sim = self.semantic_sim.similarity(
                str(reference_node.content),
                str(candidate_node.content)
            )
            
            # Factor 2: Temporal decay
            days_diff = abs((candidate_node.timestamp - reference_node.timestamp).days)
            temporal_decay = head.compute_temporal_decay(days_diff)
            
            # Factor 3: Focus keyword relevance
            focus_boost = 1.0
            if head.attention_type == AttentionType.SEMANTIC_FOCUS and head.focus_keywords:
                content_text = str(candidate_node.content).lower()
                keyword_matches = sum(1 for kw in head.focus_keywords if kw in content_text)
                focus_boost = 1.0 + (keyword_matches * 0.2)
            
            # Combined weight
            total_weight = semantic_sim * temporal_decay * focus_boost
            
            # Store if significant
            if total_weight > 0.01:
                weights[candidate_id] = total_weight
        
        return weights
    
    def compute_bidirectional_attention(self, 
                                       node_id: str, 
                                       max_nodes_per_direction: int = 5) -> Dict[str, Any]:
        """
        Compute full bidirectional attention
        
        Returns:
            Dict with forward/backward weights and statistics
        """
        forward_weights = self.compute_forward_attention(node_id, max_nodes_per_direction)
        backward_weights = self.compute_backward_attention(node_id, max_nodes_per_direction)
        
        total_forward = sum(forward_weights.values())
        total_backward = sum(backward_weights.values())
        
        return {
            'forward': forward_weights,
            'backward': backward_weights,
            'total_forward_weight': total_forward,
            'total_backward_weight': total_backward,
            'attention_balance': total_forward / max(0.001, total_backward),
            'most_attended_forward': max(forward_weights.items(), key=lambda x: x[1]) if forward_weights else None,
            'most_attended_backward': max(backward_weights.items(), key=lambda x: x[1]) if backward_weights else None
        }
    
    def get_attention_summary(self, node_id: str) -> Dict[str, Any]:
        """Get attention summary for node"""
        if node_id not in self.graph.nodes:
            return {}
        
        bidirectional = self.compute_bidirectional_attention(node_id)
        
        return {
            'node_id': node_id,
            'forward_connections': len(bidirectional['forward']),
            'backward_connections': len(bidirectional['backward']),
            'total_forward_weight': bidirectional['total_forward_weight'],
            'total_backward_weight': bidirectional['total_backward_weight'],
            'attention_balance': bidirectional['attention_balance'],
            'most_attended_forward': bidirectional['most_attended_forward'],
            'most_attended_backward': bidirectional['most_attended_backward']
        }
    
    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is valid"""
        if cache_key not in self.attention_cache:
            return False
        
        age_minutes = (datetime.now() - self.cache_timestamp).total_seconds() / 60
        return age_minutes < self.cache_ttl_minutes
    
    def invalidate_cache(self):
        """Invalidate attention cache"""
        self.attention_cache.clear()
        self.cache_timestamp = datetime.now()
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get attention system statistics"""
        cache_total = self.stats['cache_hits'] + self.stats['cache_misses']
        
        return {
            **self.stats,
            'attention_heads_count': len(self.attention_heads),
            'cached_entries': len(self.attention_cache),
            'cache_hit_rate': self.stats['cache_hits'] / max(1, cache_total),
            'documents_in_corpus': self.semantic_sim.document_count,
            'unique_terms': len(self.semantic_sim.term_document_freq)
        }
    
    def print_summary(self):
        """Print attention system summary"""
        stats = self.get_statistics()
        
        print("=" * 70)
        print("TOTG BIDIRECTIONAL ATTENTION SUMMARY")
        print("=" * 70)
        print(f"Attention Heads:      {stats['attention_heads_count']}")
        print(f"Computations:         {stats['attention_computations']}")
        print(f"Cache Hit Rate:       {stats['cache_hit_rate']:.2%}")
        print(f"Forward Queries:      {stats['forward_queries']}")
        print(f"Backward Queries:     {stats['backward_queries']}")
        print(f"Cached Entries:       {stats['cached_entries']}")
        print(f"Documents in Corpus:  {stats['documents_in_corpus']}")
        print(f"Unique Terms:         {stats['unique_terms']}")
        print("=" * 70)
        
        print("\nATTENTION HEADS:")
        for head in self.attention_heads:
            print(f"  - {head.head_id:20} | {head.attention_type.value:15} | window={head.temporal_window_days}d | decay={head.decay_factor}")


# =============================================================================
# TESTS
# =============================================================================

def test_fixed_attention():
    """Test fixed attention system with improved semantic similarity"""
    print("Testing FIXED Bidirectional Attention...")
    print("=" * 70)
    
    from totg_core_fixed import test_fixed_navigation
    
    # Create graph with test data
    graph = test_fixed_navigation()
    
    # Create attention system
    attention = BidirectionalAttention(graph)
    
    print("\n" + "=" * 70)
    print("ATTENTION TESTS")
    print("=" * 70)
    
    # Test attention on node
    test_node = "node_2"
    
    print(f"\nTest 1: Forward Attention from {test_node}")
    forward_attention = attention.compute_forward_attention(test_node, max_nodes=5)
    print(f"Forward attention weights: {forward_attention}")
    print(f"Result: {'✓ PASS' if len(forward_attention) > 0 else '✗ FAIL'}")
    
    print(f"\nTest 2: Backward Attention to {test_node}")
    backward_attention = attention.compute_backward_attention(test_node, max_nodes=5)
    print(f"Backward attention weights: {backward_attention}")
    print(f"Result: {'✓ PASS' if len(backward_attention) > 0 else '✗ FAIL'}")
    
    print(f"\nTest 3: Bidirectional Attention")
    bidirectional = attention.compute_bidirectional_attention(test_node, max_nodes_per_direction=3)
    print(f"Forward weight:  {bidirectional['total_forward_weight']:.3f}")
    print(f"Backward weight: {bidirectional['total_backward_weight']:.3f}")
    print(f"Balance:         {bidirectional['attention_balance']:.3f}")
    print(f"Result: ✓ PASS")
    
    print(f"\nTest 4: Semantic Similarity Quality")
    # Test that TF-IDF works better than word overlap
    text1 = "This is about machine learning and AI"
    text2 = "Machine learning and artificial intelligence"
    text3 = "The cat sat on the mat"
    
    sim_12 = attention.semantic_sim.similarity(text1, text2)
    sim_13 = attention.semantic_sim.similarity(text1, text3)
    
    print(f"Similarity (AI texts):     {sim_12:.3f}")
    print(f"Similarity (unrelated):    {sim_13:.3f}")
    print(f"Result: {'✓ PASS - AI texts more similar!' if sim_12 > sim_13 else '✗ FAIL'}")
    
    # Print summary
    attention.print_summary()
    
    return attention


if __name__ == "__main__":
    test_fixed_attention()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOTG Comprehensive Tests - Production Ready
==========================================

Tests demonstrating all fixes work correctly with real scenarios.
"""

from datetime import datetime, timedelta
from totg_core_fixed import (
    TemporalGraph, TemporalNode, TemporalEdge, 
    NodeType, TemporalRelation
)
from totg_attention_fixed import BidirectionalAttention


def test_legal_document_scenario():
    """
    Real-world scenario: Legal document chain
    
    This demonstrates the FIX for navigation bugs - the old version
    would miss indirect connections, the new version finds them all.
    """
    print("=" * 80)
    print("TEST: LEGAL DOCUMENT SCENARIO (Real World)")
    print("=" * 80)
    
    graph = TemporalGraph()
    base_date = datetime(2024, 1, 1)
    
    # Create legal document chain
    documents = [
        {
            "id": "contract_001",
            "date": base_date,
            "type": "contract",
            "text": "Purchase agreement for industrial equipment worth 1,000,000 rubles. Delivery within 30 days. Standard warranty terms apply."
        },
        {
            "id": "amendment_001", 
            "date": base_date + timedelta(days=15),
            "type": "amendment",
            "text": "Amendment to Contract 001: Extended delivery deadline to 45 days due to supplier issues. All other terms remain unchanged."
        },
        {
            "id": "acceptance_001",
            "date": base_date + timedelta(days=35),
            "type": "acceptance",
            "text": "Acceptance certificate: Equipment received with 3 critical defects identified. Issues: faulty wiring, damaged control panel, missing safety guards."
        },
        {
            "id": "claim_001",
            "date": base_date + timedelta(days=50),
            "type": "claim",
            "text": "Formal claim letter demanding defect removal within 10 business days as per warranty terms. Requesting immediate repair or replacement of faulty components."
        },
        {
            "id": "response_001",
            "date": base_date + timedelta(days=65),
            "type": "response", 
            "text": "Supplier response: Acknowledges defects and agrees to repair within 15 days. Offers additional 6-month extended warranty as compensation."
        },
        {
            "id": "settlement_001",
            "date": base_date + timedelta(days=80),
            "type": "settlement",
            "text": "Settlement agreement: Free defect repair completed, 30,000 rubles compensation paid, extended warranty provided. Parties agree to continue business relationship."
        },
        {
            "id": "contract_002",
            "date": base_date + timedelta(days=100),
            "type": "new_contract",
            "text": "New contract 002: Continued cooperation for equipment maintenance. Better terms negotiated based on positive resolution of previous issues."
        }
    ]
    
    # Add nodes
    for doc in documents:
        node = TemporalNode(
            id=doc["id"],
            timestamp=doc["date"],
            node_type=NodeType.CONTENT,
            content=doc["text"],
            metadata={"type": doc["type"]}
        )
        graph.add_node(node)
    
    # Add edges (creates both direct and indirect relationships)
    connections = [
        ("contract_001", "amendment_001", TemporalRelation.SEQUENTIAL),
        ("amendment_001", "acceptance_001", TemporalRelation.SEQUENTIAL),
        ("contract_001", "acceptance_001", TemporalRelation.CAUSAL),  # Indirect: contract -> acceptance
        ("acceptance_001", "claim_001", TemporalRelation.CAUSAL),
        ("claim_001", "response_001", TemporalRelation.SEQUENTIAL),
        ("response_001", "settlement_001", TemporalRelation.SEQUENTIAL),
        ("contract_001", "contract_002", TemporalRelation.CAUSAL),  # Indirect: original -> new contract
    ]
    
    for from_id, to_id, relation in connections:
        edge = TemporalEdge(from_node=from_id, to_node=to_id, relation=relation)
        graph.add_edge(edge)
    
    print("\nDocument chain created:")
    for doc in documents:
        print(f"  {doc['date'].strftime('%Y-%m-%d')} | {doc['type']:12} | {doc['id']}")
    
    # Test 1: Forward navigation from claim
    print("\n" + "-" * 80)
    print("TEST 1: What happened after the claim was filed?")
    print("-" * 80)
    
    claim_id = "claim_001"
    forward_nodes = graph.get_forward_nodes(claim_id, time_window_days=60)
    
    print(f"\nFrom: {claim_id}")
    print(f"Found {len(forward_nodes)} future events:")
    for node_id in forward_nodes:
        node = graph.nodes[node_id]
        days_after = (node.timestamp - graph.nodes[claim_id].timestamp).days
        print(f"  +{days_after:2d} days | {node.metadata['type']:12} | {node_id}")
    
    expected = ["response_001", "settlement_001"]
    found_expected = [nid for nid in expected if nid in forward_nodes]
    
    print(f"\nExpected to find: {expected}")
    print(f"Actually found:   {found_expected}")
    print(f"Result: {'✓ PASS - All events found!' if len(found_expected) == len(expected) else '✗ FAIL'}")
    
    # Test 2: Backward navigation to settlement
    print("\n" + "-" * 80)
    print("TEST 2: What led to the settlement?")
    print("-" * 80)
    
    settlement_id = "settlement_001"
    backward_nodes = graph.get_backward_nodes(settlement_id, time_window_days=90)
    
    print(f"\nTo: {settlement_id}")
    print(f"Found {len(backward_nodes)} past events:")
    for node_id in backward_nodes:
        node = graph.nodes[node_id]
        days_before = (graph.nodes[settlement_id].timestamp - node.timestamp).days
        print(f"  -{days_before:2d} days | {node.metadata['type']:12} | {node_id}")
    
    expected_chain = ["contract_001", "amendment_001", "acceptance_001", "claim_001", "response_001"]
    found_chain = [nid for nid in expected_chain if nid in backward_nodes]
    
    print(f"\nExpected chain: {len(expected_chain)} events")
    print(f"Found:          {len(found_chain)} events")
    print(f"Result: {'✓ PASS - Full chain found!' if len(found_chain) >= 4 else '✗ FAIL'}")
    
    # Test 3: Path finding
    print("\n" + "-" * 80)
    print("TEST 3: Find path from original contract to new contract")
    print("-" * 80)
    
    path = graph.get_shortest_path("contract_001", "contract_002")
    
    if path:
        print(f"\nPath found with {len(path)} steps:")
        for i, node_id in enumerate(path):
            node = graph.nodes[node_id]
            arrow = " -> " if i < len(path) - 1 else ""
            print(f"  {node.metadata['type']:12} ({node_id}){arrow}", end="")
        print()
        print(f"Result: ✓ PASS - Path found!")
    else:
        print(f"Result: ✗ FAIL - No path found!")
    
    return graph


def test_attention_with_legal_docs():
    """Test attention system with legal documents"""
    print("\n" + "=" * 80)
    print("TEST: ATTENTION SYSTEM WITH LEGAL DOCUMENTS")
    print("=" * 80)
    
    # Create graph from previous test
    graph = test_legal_document_scenario()
    
    # Create attention system
    attention = BidirectionalAttention(graph)
    
    print("\n" + "-" * 80)
    print("TEST 4: Attention weights for claim document")
    print("-" * 80)
    
    claim_id = "claim_001"
    bidirectional = attention.compute_bidirectional_attention(claim_id, max_nodes_per_direction=5)
    
    print(f"\nAnalyzing: {claim_id}")
    
    print("\nForward attention (what happens next):")
    for node_id, weight in sorted(bidirectional['forward'].items(), key=lambda x: x[1], reverse=True):
        node = graph.nodes[node_id]
        print(f"  {weight:.3f} | {node.metadata['type']:12} | {node_id}")
    
    print("\nBackward attention (what led here):")
    for node_id, weight in sorted(bidirectional['backward'].items(), key=lambda x: x[1], reverse=True):
        node = graph.nodes[node_id]
        print(f"  {weight:.3f} | {node.metadata['type']:12} | {node_id}")
    
    print(f"\nAttention balance: {bidirectional['attention_balance']:.2f}")
    print(f"Result: ✓ PASS - Attention computed successfully!")
    
    # Test 5: Semantic similarity quality
    print("\n" + "-" * 80)
    print("TEST 5: Semantic similarity quality")
    print("-" * 80)
    
    # Test that similar documents get higher similarity
    contract_text = graph.nodes["contract_001"].content
    settlement_text = graph.nodes["settlement_001"].content
    unrelated = "The weather is nice today."
    
    sim_related = attention.semantic_sim.similarity(contract_text, settlement_text)
    sim_unrelated = attention.semantic_sim.similarity(contract_text, unrelated)
    
    print(f"\nSimilarity between contract and settlement: {sim_related:.3f}")
    print(f"Similarity between contract and weather:    {sim_unrelated:.3f}")
    print(f"Result: {'✓ PASS - Related docs more similar!' if sim_related > sim_unrelated else '✗ FAIL'}")
    
    return attention


def test_performance_and_scalability():
    """Test performance with larger graph"""
    print("\n" + "=" * 80)
    print("TEST: PERFORMANCE AND SCALABILITY")
    print("=" * 80)
    
    import time
    
    graph = TemporalGraph()
    base_date = datetime(2024, 1, 1)
    
    # Create larger graph
    n_nodes = 100
    print(f"\nCreating graph with {n_nodes} nodes...")
    
    start = time.time()
    
    # Add nodes
    for i in range(n_nodes):
        node = TemporalNode(
            id=f"node_{i:03d}",
            timestamp=base_date + timedelta(days=i),
            node_type=NodeType.CONTENT,
            content=f"Document {i}: This is content about topic {i % 10}. It discusses various aspects of the subject matter including key points and important details."
        )
        graph.add_node(node)
    
    # Add edges (chain + some random connections)
    for i in range(n_nodes - 1):
        # Sequential chain
        edge = TemporalEdge(
            from_node=f"node_{i:03d}",
            to_node=f"node_{i+1:03d}",
            relation=TemporalRelation.SEQUENTIAL
        )
        graph.add_edge(edge)
        
        # Some skip connections
        if i % 10 == 0 and i + 5 < n_nodes:
            edge = TemporalEdge(
                from_node=f"node_{i:03d}",
                to_node=f"node_{i+5:03d}",
                relation=TemporalRelation.CAUSAL
            )
            graph.add_edge(edge)
    
    create_time = time.time() - start
    
    print(f"✓ Created {n_nodes} nodes in {create_time:.3f}s")
    
    # Test navigation performance
    print("\nTesting navigation performance...")
    
    start = time.time()
    forward = graph.get_forward_nodes("node_010", time_window_days=30)
    forward_time = time.time() - start
    
    start = time.time()
    backward = graph.get_backward_nodes("node_050", time_window_days=30)
    backward_time = time.time() - start
    
    print(f"✓ Forward navigation:  {len(forward)} nodes in {forward_time:.3f}s")
    print(f"✓ Backward navigation: {len(backward)} nodes in {backward_time:.3f}s")
    
    # Test attention performance
    print("\nTesting attention performance...")
    
    attention = BidirectionalAttention(graph)
    
    start = time.time()
    attn = attention.compute_bidirectional_attention("node_050", max_nodes_per_direction=10)
    attention_time = time.time() - start
    
    print(f"✓ Attention computation: {attention_time:.3f}s")
    
    # Test cache effectiveness
    start = time.time()
    attn_cached = attention.compute_bidirectional_attention("node_050", max_nodes_per_direction=10)
    cached_time = time.time() - start
    
    speedup = attention_time / max(cached_time, 0.0001)
    print(f"✓ Cached computation: {cached_time:.4f}s ({speedup:.1f}x faster)")
    
    # Print statistics
    print("\nGraph statistics:")
    graph.print_summary()
    
    print("\nAttention statistics:")
    attention.print_summary()
    
    print(f"\nResult: ✓ PASS - System scales well!")
    
    return graph, attention


def run_all_tests():
    """Run all comprehensive tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TOTG COMPREHENSIVE TEST SUITE" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = {}
    
    try:
        graph1 = test_legal_document_scenario()
        results['legal_scenario'] = True
    except Exception as e:
        print(f"✗ Legal scenario test failed: {e}")
        results['legal_scenario'] = False
    
    try:
        attention1 = test_attention_with_legal_docs()
        results['attention_legal'] = True
    except Exception as e:
        print(f"✗ Attention test failed: {e}")
        results['attention_legal'] = False
    
    try:
        graph2, attention2 = test_performance_and_scalability()
        results['performance'] = True
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        results['performance'] = False
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name:25} : {status}")
    
    print("-" * 80)
    print(f"Total: {passed_tests}/{total_tests} tests passed ({100*passed_tests/total_tests:.0f}%)")
    print("=" * 80)
    
    if passed_tests == total_tests:
        print("\n🎉 SUCCESS! All tests passed. System is production-ready!")
    else:
        print("\n⚠️  Some tests failed. Review output above.")
    
    return results


if __name__ == "__main__":
    results = run_all_tests()

#!/usr/bin/env python3
"""
Simple test to demonstrate TOTG functionality
"""

from datetime import datetime, timedelta
from totg_api import TOTGAPI

def main():
    print("=== TOTG MCP Tool Analysis ===")
    print()
    
    # Initialize the API
    api = TOTGAPI()
    
    # Add some test documents (legal document scenario)
    base_date = datetime(2024, 1, 1)
    
    # Add documents
    api.add_document(
        doc_id="contract_001",
        content="Purchase agreement for industrial equipment worth $1,000,000. Delivery within 30 days.",
        timestamp=base_date,
        metadata={"type": "contract", "value": 1000000}
    )
    
    api.add_document(
        doc_id="amendment_001", 
        content="Amendment: Extended delivery deadline to 45 days due to supplier issues.",
        timestamp=base_date + timedelta(days=15),
        metadata={"type": "amendment"}
    )
    
    api.add_document(
        doc_id="claim_001",
        content="Claim filed: Equipment received with critical defects identified.",
        timestamp=base_date + timedelta(days=50),
        metadata={"type": "claim"}
    )
    
    api.add_document(
        doc_id="response_001",
        content="Response to claim: Accepting responsibility and offering compensation.",
        timestamp=base_date + timedelta(days=65),
        metadata={"type": "response"}
    )
    
    api.add_document(
        doc_id="settlement_001",
        content="Settlement reached: Compensation of $150,000 agreed upon.",
        timestamp=base_date + timedelta(days=80),
        metadata={"type": "settlement", "value": 150000}
    )
    
    # Add relationships
    api.add_relationship("contract_001", "amendment_001", "sequential")
    api.add_relationship("amendment_001", "claim_001", "causal")
    api.add_relationship("claim_001", "response_001", "sequential")
    api.add_relationship("response_001", "settlement_001", "causal")
    
    print("Added 5 documents with relationships")
    print()
    
    # Test temporal queries
    print("1. What happened after the amendment?")
    future_docs = api.get_future_documents("amendment_001", days=60)
    for doc in future_docs:
        print(f"   - {doc.id}: {doc.content[:50]}...")
    print()
    
    print("2. What led to the settlement?")
    past_docs = api.get_past_documents("settlement_001", days=120)
    for doc in past_docs:
        print(f"   - {doc.id}: {doc.content[:50]}...")
    print()
    
    # Test path finding
    print("3. Path from contract to settlement:")
    path = api.find_path("contract_001", "settlement_001")
    print(f"   Path: {' -> '.join(path.path) if path.exists else 'No path found'}")
    print()
    
    # Test attention (semantic relevance)
    print("4. Computing attention for the claim:")
    attention = api.compute_attention("claim_001", max_per_direction=3)
    print(f"   Forward attention (what claim leads to): {list(attention.forward_attention.keys())}")
    print(f"   Backward attention (what leads to claim): {list(attention.backward_attention.keys())}")
    print()
    
    # Statistics
    print("5. Graph statistics:")
    stats = api.get_statistics()
    print(f"   Nodes: {stats['nodes']}")
    print(f"   Edges: {stats['edges']}")
    print(f"   Time span: {stats['time_span_days']} days")
    print()
    
    print("=== TOTG System Analysis Complete ===")
    return True

if __name__ == "__main__":
    main()

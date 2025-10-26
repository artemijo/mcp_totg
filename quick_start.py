#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOTG Quick Start Guide
=====================

Copy-paste ready examples to get started immediately.
"""

from totg_api import TOTGAPI
from datetime import datetime, timedelta

def example_1_simple_document_chain():
    """Example 1: Simple document chain"""
    print("=" * 70)
    print("EXAMPLE 1: Simple Document Chain")
    print("=" * 70)
    
    api = TOTGAPI()
    
    # Add documents
    docs = [
        ("proposal", "Project proposal for new system", 0),
        ("requirements", "Detailed requirements specification", 7),
        ("design", "Technical design document", 14),
        ("implementation", "Implementation plan", 21)
    ]
    
    base_date = datetime.now()
    for doc_id, content, days_offset in docs:
        api.add_document(
            doc_id=doc_id,
            content=content,
            timestamp=base_date + timedelta(days=days_offset)
        )
    
    # Link them
    api.add_relationship("proposal", "requirements", "sequential")
    api.add_relationship("requirements", "design", "sequential")
    api.add_relationship("design", "implementation", "sequential")
    
    # Query: What comes after requirements?
    future = api.get_future_documents("requirements", days=30)
    print(f"\nWhat comes after requirements?")
    for doc in future:
        print(f"  - {doc.id}: {doc.content}")
    
    # Find path
    path = api.find_path("proposal", "implementation")
    print(f"\nPath from proposal to implementation:")
    print(f"  {' → '.join(path.path)}")
    
    return api


def example_2_legal_documents():
    """Example 2: Legal document tracking"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Legal Document Tracking")
    print("=" * 70)
    
    api = TOTGAPI()
    base_date = datetime(2024, 1, 1)
    
    # Add legal documents
    api.add_document(
        "contract_001",
        "Purchase agreement for equipment worth $1M. Delivery in 30 days.",
        base_date,
        {"type": "contract", "amount": 1000000}
    )
    
    api.add_document(
        "acceptance_001",
        "Equipment received with 3 defects identified during inspection.",
        base_date + timedelta(days=35),
        {"type": "acceptance", "defects": 3}
    )
    
    api.add_document(
        "claim_001",
        "Formal claim for defect repair within 10 days per warranty.",
        base_date + timedelta(days=50),
        {"type": "claim"}
    )
    
    api.add_document(
        "settlement_001",
        "Settlement: Free repair + $30K compensation + extended warranty.",
        base_date + timedelta(days=80),
        {"type": "settlement", "compensation": 30000}
    )
    
    # Link documents
    api.add_relationship("contract_001", "acceptance_001", "causal")
    api.add_relationship("acceptance_001", "claim_001", "causal")
    api.add_relationship("claim_001", "settlement_001", "sequential")
    
    # Query: What led to settlement?
    past = api.get_past_documents("settlement_001", days=90)
    print(f"\nWhat led to the settlement?")
    for doc in past:
        print(f"  - {doc.id} ({doc.metadata.get('type', 'unknown')})")
    
    # Compute attention
    attention = api.compute_attention("claim_001", max_per_direction=3)
    print(f"\nAttention for claim document:")
    print(f"  Forward attention: {len(attention.forward_attention)} docs")
    print(f"  Backward attention: {len(attention.backward_attention)} docs")
    print(f"  Balance: {attention.summary['attention_balance']:.2f}")
    
    return api


def example_3_customer_support():
    """Example 3: Customer support ticket tracking"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Customer Support Ticket Tracking")
    print("=" * 70)
    
    api = TOTGAPI()
    base_date = datetime.now()
    
    # Customer journey
    tickets = [
        ("ticket_001", "Customer reports login issue", 0, "open"),
        ("investigation_001", "Tech team investigates: database connection issue", 1, "investigating"),
        ("fix_001", "Database fix applied and tested", 2, "fixing"),
        ("verification_001", "Customer confirms issue resolved", 3, "resolved"),
        ("followup_001", "Follow-up email sent with satisfaction survey", 4, "closed")
    ]
    
    for ticket_id, content, days_offset, status in tickets:
        api.add_document(
            ticket_id,
            content,
            base_date + timedelta(days=days_offset),
            {"status": status}
        )
    
    # Link the chain
    for i in range(len(tickets) - 1):
        api.add_relationship(tickets[i][0], tickets[i+1][0], "sequential")
    
    # Query: Ticket resolution chain
    path = api.find_path("ticket_001", "followup_001")
    print(f"\nTicket resolution chain:")
    for i, step_id in enumerate(path.path, 1):
        doc = api.get_document(step_id)
        print(f"  {i}. {doc.id}: {doc.content[:50]}... [{doc.metadata['status']}]")
    
    # Find related tickets
    related = api.find_related_documents("investigation_001", max_results=5)
    print(f"\nRelated to investigation:")
    print(f"  Forward: {len(related.get('forward', []))} docs")
    print(f"  Backward: {len(related.get('backward', []))} docs")
    
    return api


def example_4_project_timeline():
    """Example 4: Project timeline with branches"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Project Timeline with Branches")
    print("=" * 70)
    
    api = TOTGAPI()
    base_date = datetime(2024, 1, 1)
    
    # Main timeline
    api.add_document("kickoff", "Project kickoff meeting", base_date)
    api.add_document("planning", "Sprint planning", base_date + timedelta(days=7))
    
    # Branch A: Frontend work
    api.add_document("frontend_design", "UI/UX design", base_date + timedelta(days=14))
    api.add_document("frontend_impl", "Frontend implementation", base_date + timedelta(days=21))
    
    # Branch B: Backend work
    api.add_document("backend_design", "API design", base_date + timedelta(days=14))
    api.add_document("backend_impl", "Backend implementation", base_date + timedelta(days=21))
    
    # Merge point
    api.add_document("integration", "Integration testing", base_date + timedelta(days=28))
    api.add_document("release", "Production release", base_date + timedelta(days=35))
    
    # Link main timeline
    api.add_relationship("kickoff", "planning", "sequential")
    
    # Branch from planning
    api.add_relationship("planning", "frontend_design", "branch")
    api.add_relationship("planning", "backend_design", "branch")
    
    # Parallel work
    api.add_relationship("frontend_design", "frontend_impl", "sequential")
    api.add_relationship("backend_design", "backend_impl", "sequential")
    
    # Merge to integration
    api.add_relationship("frontend_impl", "integration", "merge")
    api.add_relationship("backend_impl", "integration", "merge")
    
    # Final release
    api.add_relationship("integration", "release", "sequential")
    
    # Query: What happened after planning?
    future = api.get_future_documents("planning", days=30)
    print(f"\nWhat happened after planning? ({len(future)} branches)")
    for doc in future:
        print(f"  - {doc.id}")
    
    # Query: What led to integration?
    past = api.get_past_documents("integration", days=30)
    print(f"\nWhat led to integration? ({len(past)} parallel tracks)")
    for doc in past:
        print(f"  - {doc.id}")
    
    return api


def example_5_knowledge_graph():
    """Example 5: Building a knowledge graph"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Knowledge Graph")
    print("=" * 70)
    
    api = TOTGAPI()
    base_date = datetime(2024, 1, 1)
    
    # Add knowledge articles over time
    articles = [
        ("intro_ml", "Introduction to Machine Learning concepts and algorithms", 0),
        ("neural_nets", "Deep dive into neural networks: architecture and training", 30),
        ("cnn", "Convolutional Neural Networks for image recognition", 60),
        ("rnn", "Recurrent Neural Networks and sequence modeling", 60),
        ("transformers", "Transformer architecture and attention mechanisms", 90),
        ("llm", "Large Language Models: GPT and BERT explained", 120)
    ]
    
    for article_id, content, days_offset in articles:
        api.add_document(
            article_id,
            content,
            base_date + timedelta(days=days_offset),
            {"category": "ml"}
        )
    
    # Link knowledge progression
    api.add_relationship("intro_ml", "neural_nets", "sequential")
    api.add_relationship("neural_nets", "cnn", "branch")
    api.add_relationship("neural_nets", "rnn", "branch")
    api.add_relationship("cnn", "transformers", "causal")
    api.add_relationship("rnn", "transformers", "causal")
    api.add_relationship("transformers", "llm", "sequential")
    
    # Find learning path
    path = api.find_path("intro_ml", "llm")
    print(f"\nLearning path from intro to LLM:")
    print(f"  {' → '.join(path.path)}")
    print(f"  Path length: {path.path_length} steps")
    
    # Find prerequisites for transformers
    prereqs = api.get_past_documents("transformers", days=100)
    print(f"\nPrerequisites for learning transformers:")
    for doc in prereqs:
        print(f"  - {doc.id}")
    
    # Get statistics
    stats = api.get_statistics()
    print(f"\nKnowledge graph stats:")
    print(f"  Articles: {stats['graph']['total_nodes']}")
    print(f"  Connections: {stats['graph']['total_edges']}")
    
    return api


def run_all_examples():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "TOTG QUICK START EXAMPLES" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\nThese examples show common use cases for TOTG.")
    print("Copy and modify them for your needs!\n")
    
    example_1_simple_document_chain()
    example_2_legal_documents()
    example_3_customer_support()
    example_4_project_timeline()
    example_5_knowledge_graph()
    
    print("\n" + "=" * 70)
    print("✅ All examples complete! Pick one and start building!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_examples()

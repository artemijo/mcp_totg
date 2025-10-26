#!/usr/bin/env python3
"""
Test TotG Functionality
======================

Comprehensive test to verify if TotG tool works as intended.
"""

print('=' * 60)
print('TOTG FUNCTIONALITY TEST')
print('=' * 60)

# Test 1: Basic imports
try:
    from totg_api import TOTGAPI
    from datetime import datetime, timedelta
    print('✅ Imports successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    exit(1)

# Test 2: Basic API initialization
try:
    api = TOTGAPI()
    print('✅ API initialized successfully')
except Exception as e:
    print(f'❌ API initialization failed: {e}')
    exit(1)

# Test 3: Document creation
try:
    base_date = datetime(2024, 1, 1)
    result = api.add_document('test_doc', 'Test content', base_date)
    print(f'✅ Document creation: {result}')
except Exception as e:
    print(f'❌ Document creation failed: {e}')
    exit(1)

# Test 4: Document retrieval
try:
    doc = api.get_document('test_doc')
    if doc:
        print(f'✅ Document retrieval: {doc.id}, {doc.content}')
    else:
        print('❌ Document retrieval returned None')
except Exception as e:
    print(f'❌ Document retrieval failed: {e}')

# Test 5: List documents
try:
    docs = api.list_documents()
    print(f'✅ List documents: Found {len(docs)} documents')
except Exception as e:
    print(f'❌ List documents failed: {e}')

# Test 6: Relationship creation
try:
    api.add_document('test_doc2', 'Test content 2', base_date + timedelta(days=1))
    rel_result = api.add_relationship('test_doc', 'test_doc2', 'sequential')
    print(f'✅ Relationship creation: {rel_result}')
except Exception as e:
    print(f'❌ Relationship creation failed: {e}')

# Test 7: Graph statistics
try:
    stats = api.get_statistics()
    print(f'✅ Graph stats: {stats["graph"]["total_nodes"]} nodes, {stats["graph"]["total_edges"]} edges')
except Exception as e:
    print(f'❌ Graph statistics failed: {e}')

# Test 8: Path finding
try:
    path_result = api.find_path('test_doc', 'test_doc2')
    print(f'✅ Path finding: {path_result.exists}, path: {path_result.path}')
except Exception as e:
    print(f'❌ Path finding failed: {e}')

# Test 9: Markovian analysis
try:
    # Create more documents for Markovian test
    for i in range(3, 8):
        api.add_document(f'test_doc{i}', f'Test content {i}', base_date + timedelta(days=i))
        api.add_relationship(f'test_doc{i-1}', f'test_doc{i}', 'sequential')
    
    markovian_result = api.analyze_long_chain('test_doc', max_days=100, chunk_size_days=30)
    print(f'✅ Markovian analysis: {markovian_result.total_documents} docs, {markovian_result.num_chunks} chunks')
except Exception as e:
    print(f'❌ Markovian analysis failed: {e}')
    import traceback
    traceback.print_exc()

# Test 10: Export functionality
try:
    export_data = api.export_graph()
    print(f'✅ Export: {len(export_data["nodes"])} nodes, {len(export_data["edges"])} edges')
except Exception as e:
    print(f'❌ Export failed: {e}')

print('=' * 60)
print('BASIC FUNCTIONALITY TEST COMPLETE')
print('=' * 60)
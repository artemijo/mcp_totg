#!/usr/bin/env python3
"""
Test for Serialization Issues
===========================

Test specifically for the datetime serialization issues mentioned in the AI analysis.
"""

print('=' * 60)
print('SERIALIZATION ISSUES TEST')
print('=' * 60)

import json
from datetime import datetime, timedelta

# Test 1: Basic imports
try:
    from totg_api import TOTGAPI
    print('✅ Imports successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    exit(1)

# Test 2: Document creation with datetime
try:
    api = TOTGAPI()
    base_date = datetime(2024, 1, 1)
    
    # Test with explicit datetime object
    result = api.add_document('test_doc', 'Test content', base_date)
    print(f'✅ Document creation with datetime: {result["success"]}')
    
    # Test with ISO string
    iso_date = "2024-01-01T00:00:00Z"
    result2 = api.add_document('test_doc2', 'Test content 2', iso_date)
    print(f'✅ Document creation with ISO string: {result2["success"]}')
    
except Exception as e:
    print(f'❌ Document creation failed: {e}')
    import traceback
    traceback.print_exc()

# Test 3: Document retrieval
try:
    doc = api.get_document('test_doc')
    if doc:
        print(f'✅ Document retrieval successful: {doc.id}')
        print(f'   Timestamp type: {type(doc.timestamp)}')
        print(f'   Timestamp value: {doc.timestamp}')
    else:
        print('❌ Document retrieval returned None')
except Exception as e:
    print(f'❌ Document retrieval failed: {e}')

# Test 4: List documents
try:
    docs = api.list_documents()
    print(f'✅ List documents: Found {len(docs)} documents')
    for doc in docs:
        print(f'   - {doc.id}: {type(doc.timestamp)}')
except Exception as e:
    print(f'❌ List documents failed: {e}')

# Test 5: JSON serialization test
try:
    # Test direct serialization of document data
    doc = api.get_document('test_doc')
    if doc:
        # Convert to dict
        doc_dict = {
            'id': doc.id,
            'timestamp': doc.timestamp,
            'content': doc.content,
            'metadata': doc.metadata
        }
        
        # Try to serialize
        json_str = json.dumps(doc_dict, default=str)
        print('✅ JSON serialization successful')
        
        # Try to deserialize
        parsed = json.loads(json_str)
        print('✅ JSON deserialization successful')
        
except Exception as e:
    print(f'❌ JSON serialization failed: {e}')
    import traceback
    traceback.print_exc()

# Test 6: Export functionality
try:
    export_data = api.export_graph()
    print(f'✅ Export successful: {len(export_data["nodes"])} nodes')
    
    # Try to serialize export data
    json_str = json.dumps(export_data, default=str)
    print('✅ Export JSON serialization successful')
    
except Exception as e:
    print(f'❌ Export failed: {e}')
    import traceback
    traceback.print_exc()

# Test 7: Markovian analysis with datetime
try:
    # Create more documents for Markovian test
    for i in range(3, 8):
        api.add_document(f'test_doc{i}', f'Test content {i}', base_date + timedelta(days=i))
        api.add_relationship(f'test_doc{i-1}', f'test_doc{i}', 'sequential')
    
    markovian_result = api.analyze_long_chain('test_doc', max_days=100, chunk_size_days=30)
    print(f'✅ Markovian analysis successful: {markovian_result.total_documents} docs')
    
    # Try to serialize Markovian result
    if hasattr(markovian_result, 'get_summary'):
        summary = markovian_result.get_summary()
        print('✅ Markovian summary generation successful')
    
except Exception as e:
    print(f'❌ Markovian analysis failed: {e}')
    import traceback
    traceback.print_exc()

print('=' * 60)
print('SERIALIZATION TEST COMPLETE')
print('=' * 60)
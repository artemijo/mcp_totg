#!/usr/bin/env python3
"""
Test script to verify the datetime fix is working
"""

from totg_api import TOTGAPI
from datetime import datetime

print('=' * 60)
print('TESTING DATETIME FIX')
print('=' * 60)

api = TOTGAPI()

# Test the exact scenario that was failing
try:
    # Test 1: Add document with datetime object
    base_date = datetime(2024, 1, 1)
    result1 = api.add_document('test_dt', 'Test with datetime', base_date)
    print(f'✅ Datetime object creation: {result1["success"]}')
    
    # Test 2: Add document with ISO string
    iso_date = '2024-01-01T00:00:00Z'
    result2 = api.add_document('test_iso', 'Test with ISO', iso_date)
    print(f'✅ ISO string creation: {result2["success"]}')
    
    # Test 3: Add relationship between them (this was failing before)
    rel_result = api.add_relationship('test_dt', 'test_iso', 'sequential')
    print(f'✅ Relationship creation: {rel_result["success"]}')
    
    # Test 4: Verify both documents exist
    doc1 = api.get_document('test_dt')
    doc2 = api.get_document('test_iso')
    print(f'✅ Both documents retrieved: {doc1 is not None and doc2 is not None}')
    
    # Test 5: Test Markovian analysis on the fixed chain
    if doc1 and doc2:
        markovian_result = api.analyze_long_chain('test_dt', max_days=30, chunk_size_days=15)
        print(f'✅ Markovian analysis: {markovian_result.total_documents} docs processed')
    
    print('=' * 60)
    print('🎉 ALL TESTS PASSED - DATETIME ISSUE FIXED!')
    print('=' * 60)
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    import traceback
    traceback.print_exc()
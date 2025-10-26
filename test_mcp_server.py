#!/usr/bin/env python3
"""
Test MCP Server Functionality
===========================

Test if MCP server tools are available and working.
"""

print('=' * 60)
print('MCP SERVER FUNCTIONALITY TEST')
print('=' * 60)

# Test 1: Import MCP server
try:
    from totg_mcp_server import TOOLS
    print('✅ MCP server import successful')
except Exception as e:
    print(f'❌ MCP server import failed: {e}')
    exit(1)

# Test 2: Check tool availability
print(f'✅ MCP server has {len(TOOLS)} tools available')

# Test 3: Check Markovian tools
markovian_tools = [t for t in TOOLS if 'markovian' in t.name]
print(f'✅ Found {len(markovian_tools)} Markovian tools:')
for tool in markovian_tools:
    print(f'  - {tool.name}')

# Test 4: Check basic tools
basic_tools = ['totg_add_document', 'totg_get_document', 'totg_list_documents']
for tool_name in basic_tools:
    tool_exists = any(t.name == tool_name for t in TOOLS)
    status = '✅' if tool_exists else '❌'
    availability = "Available" if tool_exists else "Missing"
    print(f'{status} {tool_name}: {availability}')

# Test 5: Check advanced tools
advanced_tools = ['totg_analyze_long_chain', 'totg_compute_attention', 'totg_find_path']
for tool_name in advanced_tools:
    tool_exists = any(t.name == tool_name for t in TOOLS)
    status = '✅' if tool_exists else '❌'
    availability = "Available" if tool_exists else "Missing"
    print(f'{status} {tool_name}: {availability}')

print('=' * 60)
print('MCP SERVER TEST COMPLETE')
print('=' * 60)
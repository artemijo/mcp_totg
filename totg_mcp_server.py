#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOTG MCP Server
==============

Model Context Protocol server for TOTG temporal graph system.
Exposes all TOTG functionality as MCP tools.

Installation:
    pip install mcp

Usage:
    python totg_mcp_server.py

In Claude Desktop config:
    {
      "mcpServers": {
        "totg": {
          "command": "python",
          "args": ["/path/to/totg_mcp_server.py"]
        }
      }
    }
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: MCP not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# TOTG imports
from totg_api import TOTGAPI


# Initialize TOTG API
api = TOTGAPI()

# Initialize MCP Server
server = Server("totg-server")


# =============================================================================
# MCP TOOL DEFINITIONS
# =============================================================================

TOOLS = [
    Tool(
        name="totg_add_document",
        description="Add a document to the temporal graph with timestamp and metadata",
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "Unique document identifier"
                },
                "content": {
                    "type": "string",
                    "description": "Document content (text)"
                },
                "timestamp": {
                    "type": "string",
                    "description": "ISO format timestamp (optional, defaults to now)",
                    "default": None
                },
                "metadata": {
                    "type": "object",
                    "description": "Optional metadata dictionary",
                    "default": {}
                }
            },
            "required": ["doc_id", "content"]
        }
    ),
    
    Tool(
        name="totg_add_relationship",
        description="Add a relationship/edge between two documents",
        inputSchema={
            "type": "object",
            "properties": {
                "from_doc": {
                    "type": "string",
                    "description": "Source document ID"
                },
                "to_doc": {
                    "type": "string",
                    "description": "Target document ID"
                },
                "relation_type": {
                    "type": "string",
                    "enum": ["sequential", "causal", "concurrent", "branch", "merge"],
                    "description": "Type of relationship",
                    "default": "sequential"
                },
                "weight": {
                    "type": "number",
                    "description": "Edge weight",
                    "default": 1.0
                }
            },
            "required": ["from_doc", "to_doc"]
        }
    ),
    
    Tool(
        name="totg_get_future_documents",
        description="Get documents that happen after (are reachable from) a given document",
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "Source document ID"
                },
                "days": {
                    "type": "integer",
                    "description": "Time window in days",
                    "default": 30
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "default": 50
                }
            },
            "required": ["doc_id"]
        }
    ),
    
    Tool(
        name="totg_get_past_documents",
        description="Get documents that happened before (can reach) a given document",
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "Target document ID"
                },
                "days": {
                    "type": "integer",
                    "description": "Time window in days",
                    "default": 30
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "default": 50
                }
            },
            "required": ["doc_id"]
        }
    ),
    
    Tool(
        name="totg_find_path",
        description="Find path between two documents in the temporal graph",
        inputSchema={
            "type": "object",
            "properties": {
                "from_doc": {
                    "type": "string",
                    "description": "Start document ID"
                },
                "to_doc": {
                    "type": "string",
                    "description": "End document ID"
                },
                "max_hops": {
                    "type": "integer",
                    "description": "Maximum path length",
                    "default": 10
                }
            },
            "required": ["from_doc", "to_doc"]
        }
    ),
    
    Tool(
        name="totg_compute_attention",
        description="Compute bidirectional attention weights for a document (semantic relevance)",
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "Document ID to analyze"
                },
                "max_per_direction": {
                    "type": "integer",
                    "description": "Max results per direction (forward/backward)",
                    "default": 10
                }
            },
            "required": ["doc_id"]
        }
    ),
    
    Tool(
        name="totg_find_related_documents",
        description="Find semantically related documents using attention weights",
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "Source document ID"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "default": 10
                },
                "direction": {
                    "type": "string",
                    "enum": ["forward", "backward", "both"],
                    "description": "Search direction",
                    "default": "both"
                }
            },
            "required": ["doc_id"]
        }
    ),
    
    Tool(
        name="totg_get_document",
        description="Get a single document by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "Document ID"
                }
            },
            "required": ["doc_id"]
        }
    ),
    
    Tool(
        name="totg_list_documents",
        description="List all documents in the graph",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum documents to return",
                    "default": 100
                }
            }
        }
    ),
    
    Tool(
        name="totg_get_statistics",
        description="Get graph statistics (nodes, edges, performance metrics)",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    
    Tool(
        name="totg_export_graph",
        description="Export entire graph as JSON",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    )
]


# =============================================================================
# MCP HANDLERS
# =============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available TOTG tools"""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        # Parse timestamp if provided
        if "timestamp" in arguments and arguments["timestamp"]:
            arguments["timestamp"] = datetime.fromisoformat(arguments["timestamp"])
        
        # Route to appropriate handler
        if name == "totg_add_document":
            result = api.add_document(**arguments)
            
        elif name == "totg_add_relationship":
            result = api.add_relationship(**arguments)
            
        elif name == "totg_get_future_documents":
            docs = api.get_future_documents(**arguments)
            result = {
                "count": len(docs),
                "documents": [
                    {
                        "id": doc.id,
                        "timestamp": doc.timestamp,
                        "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                        "metadata": doc.metadata
                    }
                    for doc in docs
                ]
            }
            
        elif name == "totg_get_past_documents":
            docs = api.get_past_documents(**arguments)
            result = {
                "count": len(docs),
                "documents": [
                    {
                        "id": doc.id,
                        "timestamp": doc.timestamp,
                        "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                        "metadata": doc.metadata
                    }
                    for doc in docs
                ]
            }
            
        elif name == "totg_find_path":
            path_result = api.find_path(**arguments)
            result = {
                "from": path_result.from_node,
                "to": path_result.to_node,
                "path": path_result.path,
                "length": path_result.path_length,
                "exists": path_result.exists
            }
            
        elif name == "totg_compute_attention":
            attention = api.compute_attention(**arguments)
            result = {
                "node_id": attention.node_id,
                "forward_attention": attention.forward_attention,
                "backward_attention": attention.backward_attention,
                "summary": attention.summary
            }
            
        elif name == "totg_find_related_documents":
            related = api.find_related_documents(**arguments)
            result = {
                "forward": related.get("forward", []),
                "backward": related.get("backward", [])
            }
            
        elif name == "totg_get_document":
            doc = api.get_document(**arguments)
            if doc:
                result = {
                    "id": doc.id,
                    "timestamp": doc.timestamp,
                    "type": doc.type,
                    "content": doc.content,
                    "metadata": doc.metadata
                }
            else:
                result = {"error": "Document not found"}
                
        elif name == "totg_list_documents":
            docs = api.list_documents(**arguments)
            result = {
                "count": len(docs),
                "documents": [
                    {
                        "id": doc.id,
                        "timestamp": doc.timestamp,
                        "type": doc.type,
                        "content": doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
                    }
                    for doc in docs
                ]
            }
            
        elif name == "totg_get_statistics":
            result = api.get_statistics()
            
        elif name == "totg_export_graph":
            result = api.export_graph()
            
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }, indent=2)
        )]


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def cli_entry():
    """Entry point for uvx/pip install"""
    import asyncio
    asyncio.run(main())

if __name__ == "__main__":
    cli_entry()

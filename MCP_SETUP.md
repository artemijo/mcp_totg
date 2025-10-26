# TOTG MCP Server Setup Guide

## What is MCP?

**Model Context Protocol (MCP)** is a standard protocol that allows AI assistants like Claude to interact with external tools and data sources. The TOTG MCP server exposes all TOTG functionality as tools that Claude can use.

---

## Installation

### 1. Install MCP Library

```bash
pip install mcp
```

### 2. Verify Installation

```bash
python3 totg_mcp_server.py
# Should start the MCP server (press Ctrl+C to stop)
```

---

## Configuration for Claude Desktop

### For macOS/Linux

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "totg": {
      "command": "python3",
      "args": ["/absolute/path/to/totg_mcp_server.py"]
    }
  }
}
```

### For Windows

Edit `%APPDATA%/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "totg": {
      "command": "python",
      "args": ["C:\\path\\to\\totg_mcp_server.py"]
    }
  }
}
```

**Important:** Use the absolute path to `totg_mcp_server.py`

---

## Available Tools

Once configured, Claude will have access to these TOTG tools:

### Document Management
- **totg_add_document** - Add document to temporal graph
- **totg_get_document** - Get document by ID
- **totg_list_documents** - List all documents

### Relationships
- **totg_add_relationship** - Create relationship between documents

### Temporal Queries
- **totg_get_future_documents** - Get documents after a given one
- **totg_get_past_documents** - Get documents before a given one
- **totg_find_path** - Find path between two documents

### Semantic Analysis
- **totg_compute_attention** - Compute semantic attention weights
- **totg_find_related_documents** - Find related documents

### Graph Analysis
- **totg_get_statistics** - Get graph statistics
- **totg_export_graph** - Export entire graph

---

## Example Usage with Claude

Once configured, you can ask Claude:

```
"Please add these legal documents to TOTG and find the relationship between them:
- Contract signed on 2024-01-01
- Claim filed on 2024-02-15
- Settlement reached on 2024-03-20"
```

Claude will use the TOTG tools to:
1. Add each document
2. Create relationships
3. Analyze the timeline
4. Report findings

---

## Testing the MCP Server

### Test 1: Direct Run (Manual Test)

```bash
python3 totg_mcp_server.py
# Server starts and waits for input
# Press Ctrl+C to stop
```

### Test 2: With Claude Desktop

1. Configure as shown above
2. Restart Claude Desktop
3. In a new conversation, ask:
   ```
   "Can you list the available TOTG tools?"
   ```
4. Claude should list all 11 TOTG tools

---

## Troubleshooting

### Server Won't Start

**Error:** `ModuleNotFoundError: No module named 'mcp'`

**Solution:**
```bash
pip3 install mcp
```

### Claude Can't See Tools

**Check:**
1. Is the path in config correct? (use absolute path)
2. Did you restart Claude Desktop after config change?
3. Try running the server manually first to check for errors

### Permission Errors

**On Unix/Linux:**
```bash
chmod +x totg_mcp_server.py
```

---

## Advanced Configuration

### Custom Port (if needed)

The server uses stdio by default (no port needed). If you need network access, modify the server code.

### Logging

Add logging to debug issues:

```python
# In totg_mcp_server.py
import logging
logging.basicConfig(level=logging.DEBUG, filename='/tmp/totg_mcp.log')
```

---

## Security Notes

1. **Local Only:** The MCP server runs locally on your machine
2. **No Network:** Uses stdio, no network ports exposed
3. **File Access:** Only accesses TOTG data, no file system access

---

## Example Session

```
User: "Add a document about project planning"

Claude: [Uses totg_add_document]
"I've added the document with ID 'project_planning_001'"

User: "What documents are in the graph now?"

Claude: [Uses totg_list_documents]
"There are 1 documents:
- project_planning_001: about project planning"

User: "Add another document about implementation and link them"

Claude: [Uses totg_add_document, then totg_add_relationship]
"I've added 'implementation_001' and created a sequential relationship from planning to implementation"

User: "What comes after planning?"

Claude: [Uses totg_get_future_documents]
"After project_planning_001, these documents follow:
- implementation_001"
```

---

## Performance

- **Startup:** <1 second
- **Per-tool call:** <0.1 seconds typically
- **Memory:** ~50MB for typical usage

---

## Compatibility

- **Python:** 3.8+
- **Claude Desktop:** Latest version
- **OS:** macOS, Linux, Windows

---

## Next Steps

1. Configure Claude Desktop
2. Restart Claude
3. Start using TOTG tools in conversations!

For more details on TOTG functionality, see `README.md`

---

**Need Help?** Check the logs in Claude Desktop's developer console.

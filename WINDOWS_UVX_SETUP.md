# TOTG MCP Server - Windows UVX Setup

## Quick Setup for Windows

### 1. Verify UV Installation

```powershell
# Check if you have uv installed
uv --version

# You should see something like: uv 0.5.29
```

### 2. Run TOTG MCP Server with UV

Your MCP server is now ready to run with UV! Here are the working methods:

#### Method 1: Direct Python with UV (Recommended)
```powershell
cd "C:\Users\andrew\Documents\MCP\totg_complete"
uv run python totg_mcp_server.py
```

#### Method 2: Using the Script Entry Point
```powershell
cd "C:\Users\andrew\Documents\MCP\totg_complete"
uv run totg-mcp
```

### 3. Claude Desktop Configuration

Edit `%APPDATA%/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "totg": {
      "command": "uv",
      "args": ["run", "python", "C:\\Users\\andrew\\Documents\\MCP\\totg_complete\\totg_mcp_server.py"]
    }
  }
}
```

Or using the script entry point:
```json
{
  "mcpServers": {
    "totg": {
      "command": "uv",
      "args": ["run", "--from", "C:\\Users\\andrew\\Documents\\MCP\\totg_complete", "totg-mcp"]
    }
  }
}
```

### 4. Test Your Setup

#### Test 1: Direct Server Run
```powershell
cd "C:\Users\andrew\Documents\MCP\totg_complete"
uv run python totg_mcp_server.py
# Server will start and wait for MCP connections
# Press Ctrl+C to stop
```

#### Test 2: With Claude Desktop
1. Update your Claude Desktop config as shown above
2. Restart Claude Desktop
3. Start a new conversation
4. Ask: "What TOTG tools are available?"
5. You should see all 11 TOTG tools listed

## Troubleshooting Windows Issues

### Issue: "uv command not found"
**Solution**: 
```powershell
# Check where uv is installed
Get-Command uv

# If not found, install via winget
winget install astral-sh.uv
```

### Issue: "Multiple top-level modules discovered"
**Status**: ✅ Fixed - Updated pyproject.toml with explicit module specification

### Issue: "Python version not supported"
**Status**: ✅ Fixed - Updated requires-python to ">=3.10" in pyproject.toml

### Issue: Path Problems in Claude Desktop
**Solution**: Use double backslashes in Windows paths:
```json
"args": ["run", "python", "C:\\Users\\andrew\\Documents\\MCP\\totg_complete\\totg_mcp_server.py"]
```

## What We Fixed

1. ✅ **Python Version Requirement**: Changed from `>=3.8` to `>=3.10` (mcp package requirement)
2. ✅ **License Format**: Changed from `{text = "MIT"}` to `"MIT"` (modern format)
3. ✅ **Module Specification**: Added explicit `py-modules` to avoid conflicts
4. ✅ **UV Integration**: Confirmed working with `uv run python` command

## Benefits of UV vs Python3

| Feature | UV | Python3 |
|---------|-----|----------|
| **Environment Isolation** | ✅ Automatic temporary environment | ❌ System-wide dependencies |
| **Dependency Management** | ✅ Auto-installs mcp and numpy | ❌ Manual pip install required |
| **Version Conflicts** | ✅ No conflicts with other tools | ❌ Possible with other MCP servers |
| **Setup Simplicity** | ✅ One command | ❌ Multiple pip install steps |
| **Professional** | ✅ Modern Python packaging | ❌ Traditional approach |

## Summary

Your TOTG MCP server is now fully compatible with UV! The key changes made:

1. **Updated `pyproject.toml`** for modern Python packaging
2. **Fixed module discovery** by explicitly specifying required modules
3. **Updated Python version requirement** to match MCP package requirements
4. **Verified UV integration** works on your Windows system

You can now run your temporal document management MCP server with modern, dependency-isolated UV packaging!

---

**Next Steps:**
1. Test the server with `uv run python totg_mcp_server.py`
2. Update your Claude Desktop config to use UV
3. Enjoy your professional, modern MCP server setup!

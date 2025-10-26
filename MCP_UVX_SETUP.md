# TOTG MCP Server - UVX Setup Guide

## What is UVX?

**UVX** is a modern Python application launcher that runs Python packages in isolated environments without manual installation. It's like `npx` for Python.

## UVX Installation

```bash
# Install uvx (comes with uv package manager)
pip install uv

# Or install uv directly (includes uvx)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Running TOTG MCP Server with UVX

### Method 1: Local Directory (Recommended for Development)

```bash
# Run from your project directory
uvx --from . totg-mcp

# Or specify the script directly
uvx python totg_mcp_server.py
```

### Method 2: Install in Editable Mode

```bash
# Install in development mode with uvx
uvx --editable . totg-mcp

# This creates a link to your local code for easy testing
```

### Method 3: From Git Repository (When Published)

```bash
# Run directly from GitHub (when you publish it)
uvx --from git+https://github.com/yourusername/totg-complete.git totg-mcp

# Or from PyPI (when published)
uvx totg-mcp
```

## Claude Desktop Configuration with UVX

### For Windows

Edit `%APPDATA%/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "totg": {
      "command": "uvx",
      "args": ["--from", "C:\\Users\\andrew\\Documents\\MCP\\totg_complete", "totg-mcp"]
    }
  }
}
```

### Alternative: Direct Python with UVX

```json
{
  "mcpServers": {
    "totg": {
      "command": "uvx",
      "args": ["python", "C:\\Users\\andrew\\Documents\\MCP\\totg_complete\\totg_mcp_server.py"]
    }
  }
}
```

## Advantages of UVX

1. **No Installation Required**: Runs in temporary environment
2. **Dependency Isolation**: No conflicts with system Python
3. **Version Management**: Easy to test different versions
4. **Cross-Platform**: Works the same on Windows, macOS, Linux
5. **Auto-Cleanup**: Temporary environments are cleaned up automatically

## Testing UVX Setup

```bash
# Test 1: Direct run
uvx --from . python totg_mcp_server.py

# Test 2: Using the script entry point
uvx --from . totg-mcp

# Test 3: Install and run
uvx pip install -e .
uvx totg-mcp
```

## Troubleshooting UVX

### Error: "No module named 'totg_api'"
**Solution**: Make sure all your Python files are in the same directory and uvx can find them.

### Error: "Command not found: uvx"
**Solution**: Install uv first:
```bash
pip install uv
```

### Error: "Can't find pyproject.toml"
**Solution**: Run uvx from the directory containing `pyproject.toml` or specify the path with `--from`.

## Publishing to PyPI (Optional)

If you want to make your MCP server available to others:

1. **Update `pyproject.toml`** with your actual details
2. **Build the package**:
   ```bash
   uvx build
   ```

3. **Upload to PyPI**:
   ```bash
   uvx twine upload dist/*
   ```

4. **Others can then run**:
   ```bash
   uvx totg-mcp
   ```

## Development Workflow with UVX

```bash
# 1. Make changes to your code
# 2. Test immediately with uvx
uvx --from . totg-mcp

# 3. Update dependencies in pyproject.toml if needed
# 4. Test again
uvx --from . totg-mcp

# 5. When ready, install for Claude Desktop
# Update the config and restart Claude
```

## Comparison: UVX vs Python3

| Feature | UVX | Python3 |
|---------|-----|----------|
| **Environment Isolation** | ✅ Automatic | ❌ System-wide |
| **Dependency Management** | ✅ Auto-install | ❌ Manual pip install |
| **Version Conflicts** | ✅ None | ❌ Possible |
| **Setup Complexity** | ✅ Simple | ❌ Requires setup |
| **Performance** | ⚡ Fast startup | ⚡ Fastest |
| **Portability** | ✅ Cross-platform | ✅ Cross-platform |

## Recommendation

For your TOTG MCP server, **UVX is recommended** because:

1. **Clean Environment**: No dependency conflicts with other MCP servers
2. **Easy Setup**: Claude Desktop users can run it without manual installation
3. **Professional**: Modern Python packaging best practices
4. **Future-Proof**: Easy to publish and share with others

---

**Next Steps:**
1. Test uvx locally with the commands above
2. Update your Claude Desktop config to use uvx
3. Enjoy your modern, dependency-isolated MCP server!
